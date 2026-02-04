"""add_status_and_is_verified_to_organizations

Revision ID: 3e63f131a653
Revises: 3c175a219e19
Create Date: 2025-10-30 13:14:33.103986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e63f131a653'
down_revision: Union[str, Sequence[str], None] = '3c175a219e19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column to organizations table
    op.add_column('organizations', sa.Column('status', sa.String(50), nullable=True, default='pending'))
    # Add is_verified column to organizations table
    op.add_column('organizations', sa.Column('is_verified', sa.Boolean(), nullable=True, default=False))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_verified column from organizations table
    op.drop_column('organizations', 'is_verified')
    # Remove status column from organizations table
    op.drop_column('organizations', 'status')
