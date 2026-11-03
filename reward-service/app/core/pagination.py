import base64
from datetime import datetime
from typing import Generic, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import tuple_

T = TypeVar("T")

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


class Page(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None   # None means: this is the last page


def make_cursor(time: datetime, row_id: str) -> str:
    return base64.urlsafe_b64encode(f"{time.isoformat()}|{row_id}".encode()).decode()


def read_cursor(cursor: str) -> tuple[datetime, str]:
    try:
        time_text, row_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        time = datetime.fromisoformat(time_text)
        if time.tzinfo is None:   # the DB column has a time zone, so the cursor needs one too
            raise ValueError("no time zone")
        return time, row_id
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cursor")


async def paginate(db, stmt, time_col, id_col, limit: int, cursor: str | None):
    """stmt = select(...) with filters only. Returns (rows, next_cursor), newest first."""
    if cursor:
        stmt = stmt.where(tuple_(time_col, id_col) < tuple_(*read_cursor(cursor)))
    stmt = stmt.order_by(time_col.desc(), id_col.desc()).limit(limit + 1)   # the extra row means "a next page exists"
    rows = list((await db.scalars(stmt)).all())
    next_cursor = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = make_cursor(getattr(last, time_col.key), getattr(last, id_col.key))
    return rows, next_cursor