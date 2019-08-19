"""add admin user rights models

Revision ID: 4278973a8f0e
Revises: bff45fe79727
Create Date: 2018-11-05 18:27:00.485319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4278973a8f0e'
down_revision = 'bff45fe79727'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_module',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('module_id', sa.String(length=32), server_default='', nullable=False),
    sa.Column('name', sa.String(length=64), server_default='', nullable=False),
    sa.Column('module_url', sa.String(length=128), server_default='', nullable=False),
    sa.Column('level', sa.String(length=64), server_default='0', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('module_id')
    )
    op.create_table('admin_rights',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('rights_id', sa.String(length=4), server_default='', nullable=False),
    sa.Column('name', sa.String(length=64), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('rights_id')
    )
    op.create_table('admin_user_module_rights',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('user_mudule_rights_id', sa.String(length=32), server_default='', nullable=False),
    sa.Column('user_id', sa.String(length=64), server_default='', nullable=False),
    sa.Column('module_id', sa.String(length=32), server_default='', nullable=False),
    sa.Column('rights_id_list', sa.String(length=64), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_mudule_rights_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin_user_module_rights')
    op.drop_table('admin_rights')
    op.drop_table('admin_module')
    # ### end Alembic commands ###