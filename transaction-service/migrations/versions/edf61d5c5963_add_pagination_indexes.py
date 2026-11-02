"""add pagination indexes

Revision ID: edf61d5c5963
Revises: 32cb4f3a48c5
Create Date: 2026-11-02 22:37:09.557865

""" 
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edf61d5c5963'
down_revision: Union[str, Sequence[str], None] = '32cb4f3a48c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index("ix_transaction_timestamp_id", "transaction", ["timestamp", "id"],
                        postgresql_concurrently=True, if_not_exists=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_transaction_timestamp_id", table_name="transaction",
                      postgresql_concurrently=True, if_exists=True)
