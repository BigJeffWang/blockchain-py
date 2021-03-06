"""add apitokenmodel

Revision ID: a86578bd13a1
Revises: 8ca29cde732e
Create Date: 2018-08-31 17:37:15.968181

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a86578bd13a1'
down_revision = '8ca29cde732e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_token',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('user_id', sa.String(length=64), server_default='', nullable=False),
    sa.Column('token_type', sa.String(length=32), server_default='', nullable=False),
    sa.Column('token', sa.String(length=128), server_default='', nullable=False),
    sa.Column('expire_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('user_type', mysql.TINYINT(display_width=4), server_default='0', nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('api_token')
    # ### end Alembic commands ###
