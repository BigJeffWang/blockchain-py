"""update TokenNodeConfModel

Revision ID: 1898ed6ce77e
Revises: a95fbc31b7c8
Create Date: 2019-01-10 10:24:05.236374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1898ed6ce77e'
down_revision = 'a95fbc31b7c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token_node_conf', sa.Column('api_key', sa.String(length=512), server_default='', nullable=False))
    op.add_column('token_node_conf', sa.Column('email', sa.String(length=512), server_default='', nullable=False))
    op.add_column('token_node_conf', sa.Column('request_type', sa.String(length=32), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('token_node_conf', 'request_type')
    op.drop_column('token_node_conf', 'email')
    op.drop_column('token_node_conf', 'api_key')
    # ### end Alembic commands ###
