"""update GameGetLotteryBlockInfoEosModel

Revision ID: fc8098eea2d6
Revises: b4dcd91a18ad
Create Date: 2019-01-15 11:28:59.108990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc8098eea2d6'
down_revision = 'b4dcd91a18ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_get_lottery_block_info_eos', sa.Column('confirm_block_num', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_get_lottery_block_info_eos', 'confirm_block_num')
    # ### end Alembic commands ###