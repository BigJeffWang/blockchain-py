"""update tx_list_eos add sender

Revision ID: b1120c4e714d
Revises: a540fdd257f5
Create Date: 2019-01-18 20:30:39.285279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1120c4e714d'
down_revision = 'a540fdd257f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tx_list_eos', sa.Column('sender', sa.String(length=18), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tx_list_eos', 'sender')
    # ### end Alembic commands ###
