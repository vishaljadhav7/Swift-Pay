"""add outbox_event table

Revision ID: 4b73a6bf9cf1
Revises: f2951c1f9d8b
Create Date: 2026-11-05 19:53:33.708156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b73a6bf9cf1'
down_revision: Union[str, Sequence[str], None] = 'f2951c1f9d8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("outbox_event"):
        return
    op.create_table(
        "outbox_event",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("topic", sa.String(100), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_outbox_event_unpublished", "outbox_event", ["created_at", "id"],
                    postgresql_where=sa.text("published_at IS NULL"))


def downgrade() -> None:
    op.drop_table("outbox_event")
