from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status


@dataclass(frozen=True)
class CurrentUser:
    id: str
    role: str

    @property
    def is_admin(self) -> bool:
        # exact match: a missing, "None" or misspelled role gets no privileges
        return self.role == "admin"


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> CurrentUser:
    """Who is calling: the gateway sets these headers after it checked the JWT."""
    if not x_user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    return CurrentUser(id=x_user_id, role=x_user_role or "")


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


def ensure_owner_or_admin(user: CurrentUser, *owner_ids: str) -> None:
    if not (user.is_admin or user.id in owner_ids):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not allowed to access this resource")