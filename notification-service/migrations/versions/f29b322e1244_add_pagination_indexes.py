"""add pagination indexes

Revision ID: f29b322e1244
Revises: ea087e0ca998
Create Date: 2026-11-02 22:13:47.836765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f29b322e1244'
down_revision: Union[str, Sequence[str], None] = 'ea087e0ca998'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index("ix_notifications_user_sent", "notifications", ["user_id", "sent_at", "id"],
                        postgresql_concurrently=True, if_not_exists=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_notifications_user_sent", table_name="notifications",
                      postgresql_concurrently=True, if_exists=True) 