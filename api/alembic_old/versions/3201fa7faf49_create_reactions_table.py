"""create_reactions_table

Revision ID: 3201fa7faf49
Revises: d50812246135
Create Date: 2024-01-09 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3201fa7faf49'
down_revision = 'd50812246135'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('message_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('emoji', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('message_id', 'user_id', 'emoji', name='uq_reaction')
    )
    
    # Create indexes
    op.create_index('ix_reactions_message_id', 'reactions', ['message_id'])
    op.create_index('ix_reactions_user_id', 'reactions', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_reactions_user_id')
    op.drop_index('ix_reactions_message_id')
    
    # Drop table
    op.drop_table('reactions')
