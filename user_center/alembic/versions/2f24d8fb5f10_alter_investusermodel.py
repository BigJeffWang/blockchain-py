"""alter investusermodel

Revision ID: 2f24d8fb5f10
Revises: 50b66fad4360
Create Date: 2018-11-02 10:52:32.746904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f24d8fb5f10'
down_revision = '50b66fad4360'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invest_users', sa.Column('nick_name', sa.String(length=64), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invest_users', 'nick_name')
    # ### end Alembic commands ###
