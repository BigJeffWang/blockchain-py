"""add merge_threshold col

Revision ID: a95fbc31b7c8
Revises: 9518e555b0d5
Create Date: 2019-01-09 14:34:58.480571

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a95fbc31b7c8'
down_revision = '9518e555b0d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_digital_instance', sa.Column('merge_threshold', mysql.INTEGER(), server_default='0', nullable=False))
    op.add_column('game_digital_template', sa.Column('merge_threshold', mysql.INTEGER(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_digital_template', 'merge_threshold')
    op.drop_column('game_digital_instance', 'merge_threshold')
    # ### end Alembic commands ###
