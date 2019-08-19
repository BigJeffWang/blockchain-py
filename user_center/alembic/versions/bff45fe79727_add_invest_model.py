"""add invest model

Revision ID: bff45fe79727
Revises: 2f24d8fb5f10
Create Date: 2018-11-05 13:31:57.241757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bff45fe79727'
down_revision = '2f24d8fb5f10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invest_users', sa.Column('avatar', sa.String(length=128), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invest_users', 'avatar')
    # ### end Alembic commands ###