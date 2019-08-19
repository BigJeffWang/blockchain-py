"""add col win_number

Revision ID: 04b834f88069
Revises: f68f9a81d67e
Create Date: 2019-02-14 22:22:12.546273

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '04b834f88069'
down_revision = 'f68f9a81d67e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('instant_game_instance', sa.Column('max_bet_ratio', mysql.INTEGER(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('instant_game_instance', 'max_bet_ratio')
    # ### end Alembic commands ###
