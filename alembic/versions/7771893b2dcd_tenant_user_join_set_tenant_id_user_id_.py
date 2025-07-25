"""tenant_user_join set tenant_id user_id nullable true

Revision ID: 7771893b2dcd
Revises: f1e1cb3aa881
Create Date: 2025-07-23 23:10:13.114412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7771893b2dcd'
down_revision: Union[str, Sequence[str], None] = 'f1e1cb3aa881'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tenant_user_join', 'tenant_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('tenant_user_join', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tenant_user_join', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('tenant_user_join', 'tenant_id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###
