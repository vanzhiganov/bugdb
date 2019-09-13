"""empty message

Revision ID: 004
Revises: 003
Create Date: 2019-09-13 03:40:13.879386

"""
from alembic import op
import sqlalchemy as sa


revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'statuses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=256), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('statuses')
