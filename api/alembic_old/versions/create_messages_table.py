"""create messages table

Revision ID: create_messages_table
Revises: create_channels_table
Create Date: 2024-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_messages_table'
down_revision = 'create_channels_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.String(length=1000), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_messages_channel_id'), 'messages', ['channel_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_channel_id'), table_name='messages')
    op.drop_table('messages') 