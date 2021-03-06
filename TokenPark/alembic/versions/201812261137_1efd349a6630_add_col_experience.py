"""add col experience

Revision ID: 1efd349a6630
Revises: d71fbd22a3a4
Create Date: 2018-12-26 11:37:17.852331

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1efd349a6630'
down_revision = 'd71fbd22a3a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_digital_instance', sa.Column('experience', mysql.INTEGER(), server_default='0', nullable=False))
    op.add_column('game_digital_template', sa.Column('experience', mysql.INTEGER(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_digital_template', 'experience')
    op.drop_column('game_digital_instance', 'experience')
    # ### end Alembic commands ###
