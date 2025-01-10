"""add channel type

Revision ID: add_channel_type
Revises: create_member_exceptions
Create Date: 2024-01-09 06:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_channel_type'
down_revision: Union[str, None] = 'create_member_exceptions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add channel type column with default value of 'public'
    op.add_column('channels', sa.Column('type', sa.String(), nullable=False, server_default='public'))


def downgrade() -> None:
    # Remove channel type column
    op.drop_column('channels', 'type') 