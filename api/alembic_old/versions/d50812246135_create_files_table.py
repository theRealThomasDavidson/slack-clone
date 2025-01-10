"""create_files_table

Revision ID: d50812246135
Revises: add_channel_type
Create Date: 2024-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd50812246135'
down_revision = 'add_channel_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'files',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),  # Path to file in filesystem
        sa.Column('uploaded_by', sa.String(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('message_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('ix_files_channel_id', 'files', ['channel_id'])
    op.create_index('ix_files_message_id', 'files', ['message_id'])
    op.create_index('ix_files_uploaded_by', 'files', ['uploaded_by'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_files_uploaded_by')
    op.drop_index('ix_files_message_id')
    op.drop_index('ix_files_channel_id')
    
    # Drop table
    op.drop_table('files')
