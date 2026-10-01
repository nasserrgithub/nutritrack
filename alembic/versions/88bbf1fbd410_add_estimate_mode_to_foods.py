"""add estimate_mode to foods

Revision ID: 88bbf1fbd410
Revises: 48d4d4c63a5d
Create Date: 2026-10-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "88bbf1fbd410"
down_revision: Union[str, Sequence[str], None] = "48d4d4c63a5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "foods",
        sa.Column("estimate_mode", sa.String(length=10), nullable=True),
    )
    op.create_unique_constraint(
        "uq_foods_name_estimate_mode", "foods", ["name", "estimate_mode"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_foods_name_estimate_mode", "foods", type_="unique")
    op.drop_column("foods", "estimate_mode")
