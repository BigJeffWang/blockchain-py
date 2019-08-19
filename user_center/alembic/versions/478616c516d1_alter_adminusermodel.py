"""alter adminusermodel

Revision ID: 478616c516d1
Revises: 94401f66dc44
Create Date: 2018-09-03 17:13:39.570152

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '478616c516d1'
down_revision = '94401f66dc44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('name', table_name='admin_users')
    op.drop_column('admin_users', 'platform')
    op.drop_column('admin_users', 'name')
    op.drop_column('admin_users', 'password')
    op.drop_column('admin_users', 'level')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin_users', sa.Column('level', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('admin_users', sa.Column('password', mysql.VARCHAR(length=64), nullable=True))
    op.add_column('admin_users', sa.Column('name', mysql.VARCHAR(length=64), nullable=True))
    op.add_column('admin_users', sa.Column('platform', mysql.VARCHAR(length=64), nullable=True))
    op.create_index('name', 'admin_users', ['name'], unique=True)
    # ### end Alembic commands ###
