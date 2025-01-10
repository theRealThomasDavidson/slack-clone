"""change_user_id_to_uuid

Revision ID: 9e22b052be94
Revises: dd24654fc4cb
Create Date: 2025-01-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e22b052be94'
down_revision = 'dd24654fc4cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a new temporary id column
    op.add_column('users', sa.Column('uuid_id', sa.String(), nullable=True))
    
    # Drop the primary key constraint
    op.drop_constraint('users_pkey', 'users')
    
    # Drop the old id column
    op.drop_column('users', 'id')
    
    # Rename uuid_id to id
    op.alter_column('users', 'uuid_id', new_column_name='id')
    
    # Add primary key constraint to the new id column
    op.create_primary_key('users_pkey', 'users', ['id'])


def downgrade() -> None:
    # Create a new temporary id column
    op.add_column('users', sa.Column('int_id', sa.Integer(), nullable=True))
    
    # Drop the primary key constraint
    op.drop_constraint('users_pkey', 'users')
    
    # Drop the old id column
    op.drop_column('users', 'id')
    
    # Rename int_id to id
    op.alter_column('users', 'int_id', new_column_name='id')
    
    # Add primary key constraint to the new id column
    op.create_primary_key('users_pkey', 'users', ['id'])
