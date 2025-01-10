"""create channels table

Revision ID: create_channels_table
Revises: 9e22b052be94
Create Date: 2024-01-09 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_channels_table'
down_revision = '9e22b052be94'  # This should point to the latest user migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'channels',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('members', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes
    op.create_index('ix_channels_name', 'channels', ['name'])
    op.create_index('ix_channels_created_by', 'channels', ['created_by'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_channels_created_by')
    op.drop_index('ix_channels_name')
    
    # Drop table
    op.drop_table('channels') 