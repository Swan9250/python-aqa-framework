"""change filfillment to fulfillment

Revision ID: 242c074468da
Revises: c98e5a562cd3
Create Date: 2025-09-23 11:14:01.435344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '242c074468da'
down_revision: Union[str, Sequence[str], None] = 'c98e5a562cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
