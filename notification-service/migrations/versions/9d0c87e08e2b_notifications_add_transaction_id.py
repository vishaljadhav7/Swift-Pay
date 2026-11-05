"""notifications add transaction_id

Revision ID: 9d0c87e08e2b
Revises: f29b322e1244
Create Date: 2026-11-05 20:20:39.819302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d0c87e08e2b'
down_revision: Union[str, Sequence[str], None] = 'f29b322e1244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE notifications ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(50)")
    # CREATE INDEX CONCURRENTLY cannot run inside a transaction, so use an autocommit block
    with op.get_context().autocommit_block():
        op.create_index("ix_notifications_transaction_id", "notifications", ["transaction_id"],
                        unique=True, postgresql_concurrently=True, if_not_exists=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_notifications_transaction_id", table_name="notifications",
                      postgresql_concurrently=True, if_exists=True)
    op.execute("ALTER TABLE notifications DROP COLUMN IF EXISTS transaction_id")