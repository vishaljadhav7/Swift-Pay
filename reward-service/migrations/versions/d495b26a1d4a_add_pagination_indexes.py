"""add pagination indexes

Revision ID: d495b26a1d4a
Revises: 40e5f646cd89
Create Date: 2026-11-02 22:09:06.666717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd495b26a1d4a'
down_revision: Union[str, Sequence[str], None] = '40e5f646cd89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index("ix_reward_user_sent", "reward", ["user_id", "sent_at", "id"],
                        postgresql_concurrently=True, if_not_exists=True)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_reward_user_sent", table_name="reward",
                      postgresql_concurrently=True, if_exists=True)