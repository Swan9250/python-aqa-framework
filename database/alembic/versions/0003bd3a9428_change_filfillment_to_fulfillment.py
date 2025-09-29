"""change filfillment to fulfillment

Revision ID: 0003bd3a9428
Revises: 242c074468da
Create Date: 2025-09-23 11:16:32.276976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003bd3a9428"
down_revision: Union[str, Sequence[str], None] = "242c074468da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "delivery_points",
        "filfillment",
        new_column_name="fulfillment",
        existing_type=sa.Boolean(),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "delivery_points",
        "fulfillment",
        new_column_name="filfillment",
        existing_type=sa.Boolean(),
    )
