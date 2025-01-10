"""add display_name and is_online to users

Revision ID: dd24654fc4cb
Revises: 676192b1c1d0
Create Date: 2025-01-08 21:48:57.378875

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dd24654fc4cb'
down_revision = '676192b1c1d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('display_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_online', sa.Boolean(), nullable=True, server_default='false'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_online')
    op.drop_column('users', 'display_name')
    # ### end Alembic commands ###