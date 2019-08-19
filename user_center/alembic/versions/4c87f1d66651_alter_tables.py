"""alter tables

Revision ID: 4c87f1d66651
Revises: 47c3c81ada65
Create Date: 2018-10-31 08:41:41.046766

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4c87f1d66651'
down_revision = '47c3c81ada65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invest_users', sa.Column('user_mobile', mysql.CHAR(length=64), server_default='', nullable=False))
    op.create_unique_constraint(None, 'invest_users', ['user_mobile'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'invest_users', type_='unique')
    op.drop_column('invest_users', 'user_mobile')
    # ### end Alembic commands ###