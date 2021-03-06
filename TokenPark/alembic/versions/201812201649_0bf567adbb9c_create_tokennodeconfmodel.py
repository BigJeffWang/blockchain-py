"""create TokenNodeConfModel

Revision ID: 0bf567adbb9c
Revises: 38cc90c6dda9
Create Date: 2018-12-20 16:49:31.072790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bf567adbb9c'
down_revision = '38cc90c6dda9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token_node_conf',
    sa.Column('_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('node_env', sa.String(length=16), server_default='dev', nullable=False),
    sa.Column('coin_id', sa.String(length=128), server_default='', nullable=False),
    sa.Column('node_url', sa.String(length=512), server_default='', nullable=False),
    sa.Column('node_port', sa.String(length=16), server_default='', nullable=False),
    sa.Column('server_status', sa.String(length=16), server_default='0', nullable=False),
    sa.Column('script_status', sa.String(length=16), server_default='0', nullable=False),
    sa.Column('mark', sa.String(length=512), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token_node_conf')
    # ### end Alembic commands ###
