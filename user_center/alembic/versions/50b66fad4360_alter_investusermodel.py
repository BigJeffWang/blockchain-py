"""alter investusermodel

Revision ID: 50b66fad4360
Revises: 3433d47a4f6d
Create Date: 2018-10-31 16:58:00.333402

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '50b66fad4360'
down_revision = '3433d47a4f6d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invest_users', sa.Column('authentication_status', mysql.TINYINT(display_width=1), server_default='1', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invest_users', 'authentication_status')
    # ### end Alembic commands ###