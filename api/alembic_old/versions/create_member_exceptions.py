"""create member exceptions table

Revision ID: create_member_exceptions
Revises: create_messages_table
Create Date: 2024-01-09 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_member_exceptions'
down_revision = 'create_messages_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create member exceptions table as a simple many-to-many
    op.create_table(
        'member_exceptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('channel_id', 'user_id', name='uq_member_exception')
    )
    
    # Create indexes
    op.create_index('ix_member_exceptions_channel_id', 'member_exceptions', ['channel_id'])
    op.create_index('ix_member_exceptions_user_id', 'member_exceptions', ['user_id'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_member_exceptions_user_id')
    op.drop_index('ix_member_exceptions_channel_id')
    
    # Drop table
    op.drop_table('member_exceptions') 