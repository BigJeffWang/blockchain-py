"""add col win_number

Revision ID: f68f9a81d67e
Revises: 3ce691fe5397
Create Date: 2019-02-14 22:18:35.365029

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f68f9a81d67e'
down_revision = '3ce691fe5397'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('instant_game_template', sa.Column('max_bet_ratio', mysql.INTEGER(), server_default='0', nullable=False))
    op.add_column('participate_in', sa.Column('win_number', sa.String(length=64), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('participate_in', 'win_number')
    op.drop_column('instant_game_template', 'max_bet_ratio')
    # ### end Alembic commands ###