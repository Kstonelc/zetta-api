"""delete tenant model status

Revision ID: d90596e1c117
Revises: 525d80d35ee1
Create Date: 2025-07-23 18:42:01.137322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d90596e1c117"
down_revision: Union[str, Sequence[str], None] = "525d80d35ee1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "tenant",
        "custom_config",
        existing_type=sa.TEXT(),
        postgresql_using="custom_config::jsonb",
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=True,
    )
    op.drop_column("tenant", "status")
    op.add_column(
        "tenant_user_join",
        sa.Column("current", sa.Boolean(), server_default="false", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("tenant_user_join", "current")
    op.add_column(
        "tenant",
        sa.Column(
            "status",
            sa.VARCHAR(length=255),
            server_default=sa.text("'unintialized'::character varying"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.alter_column(
        "tenant",
        "custom_config",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        postgresql_using="custom_config::jsonb",
        type_=sa.TEXT(),
        existing_nullable=True,
    )
    # ### end Alembic commands ###
