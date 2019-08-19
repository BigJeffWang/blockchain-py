"""create wallet_eos

Revision ID: 6ebd00e01c43
Revises: 0d990b2e222c
Create Date: 2019-01-18 17:25:34.146680

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6ebd00e01c43'
down_revision = '0d990b2e222c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wallet_eos',
    sa.Column('_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('sub_index', sa.BigInteger(), nullable=False),
    sa.Column('sub_public_address', sa.String(length=128), server_default='', nullable=False),
    sa.Column('change_index', sa.String(length=255), server_default='', nullable=False),
    sa.Column('acct_public_key_aes', sa.String(length=255), server_default='', nullable=False),
    sa.Column('coin_id', sa.String(length=128), server_default='', nullable=False),
    sa.Column('account_id', sa.String(length=64), server_default='', nullable=False),
    sa.Column('status', mysql.TINYINT(display_width=1), server_default='0', nullable=False),
    sa.Column('amount', sa.Numeric(precision=21, scale=18), server_default='0.000000000000000000', nullable=False),
    sa.Column('amount_change', sa.Numeric(precision=21, scale=18), server_default='0.000000000000000000', nullable=False),
    sa.Column('amount_frozen', sa.Numeric(precision=21, scale=18), server_default='0.000000000000000000', nullable=False),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('sub_public_address')
    )
    op.create_table('wallet_eos_gather',
    sa.Column('_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('sub_index', sa.BigInteger(), nullable=False),
    sa.Column('sub_public_address', sa.String(length=128), server_default='', nullable=False),
    sa.Column('change_index', sa.String(length=255), server_default='', nullable=False),
    sa.Column('acct_public_key_aes', sa.String(length=255), server_default='', nullable=False),
    sa.Column('coin_id', sa.String(length=128), server_default='', nullable=False),
    sa.Column('account_id', sa.String(length=64), server_default='', nullable=False),
    sa.Column('status', mysql.TINYINT(display_width=1), server_default='1', nullable=False),
    sa.Column('amount', sa.Numeric(precision=21, scale=18), server_default='0.000000000000000000', nullable=False),
    sa.Column('amount_change', sa.Numeric(precision=21, scale=18), server_default='0.000000000000000000', nullable=False),
    sa.Column('amount_frozen', sa.Numeric(precision=21, scale=18), server_default='0.000000000000000000', nullable=False),
    sa.Column('desc', sa.String(length=255), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('sub_public_address')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wallet_eos_gather')
    op.drop_table('wallet_eos')
    # ### end Alembic commands ###
