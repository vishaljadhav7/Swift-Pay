"""drop timestamp id index

Revision ID: f2951c1f9d8b
Revises: edf61d5c5963
Create Date: 2026-11-03 17:44:51.825589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2951c1f9d8b'
down_revision: Union[str, Sequence[str], None] = 'edf61d5c5963'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_transaction_timestamp_id", table_name="transaction",
                      postgresql_concurrently=True, if_exists=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index("ix_transaction_timestamp_id", "transaction", ["timestamp", "id"],
                        postgresql_concurrently=True, if_not_exists=True)
