"""delete model ForeignKey

Revision ID: a9042b6908e6
Revises: 557d885c4806
Create Date: 2025-07-22 13:37:35.388385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9042b6908e6'
down_revision: Union[str, Sequence[str], None] = '557d885c4806'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('model_model_provider_id_fkey'), 'model', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(op.f('model_model_provider_id_fkey'), 'model', 'model_provider', ['model_provider_id'], ['id'])
    # ### end Alembic commands ###
