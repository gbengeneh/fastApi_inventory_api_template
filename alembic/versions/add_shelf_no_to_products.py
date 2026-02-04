"""add shelf_no to products

Revision ID: add_shelf_no
Revises: f46005391421
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_shelf_no'
down_revision: Union[str, Sequence[str], None] = 'f46005391421'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add shelf_no column to products table
    op.add_column('products', sa.Column('shelf_no', sa.String(50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove shelf_no column from products table
    op.drop_column('products', 'shelf_no')
