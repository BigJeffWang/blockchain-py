"""create RobotInfoLibModel

Revision ID: 52002ea237a1
Revises: f23f6c02f755
Create Date: 2019-01-04 14:41:37.861546

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '52002ea237a1'
down_revision = 'f23f6c02f755'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('robot_info_lib',
    sa.Column('_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('update_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted_at', sa.DateTime(), server_default='0000-00-00 00:00:00', nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('uid', sa.String(length=64), server_default='', nullable=False),
    sa.Column('name', sa.String(length=64), server_default='', nullable=False),
    sa.Column('gender', mysql.INTEGER(), server_default='0', nullable=False),
    sa.Column('birthday', sa.String(length=256), server_default='', nullable=False),
    sa.Column('location', sa.String(length=256), server_default='', nullable=False),
    sa.Column('description', sa.String(length=512), server_default='', nullable=False),
    sa.Column('register_time', sa.String(length=256), server_default='', nullable=False),
    sa.Column('verify_type', mysql.INTEGER(), server_default='0', nullable=False),
    sa.Column('verify_info', mysql.TEXT(), nullable=True),
    sa.Column('follows_num', mysql.INTEGER(), server_default='0', nullable=False),
    sa.Column('fans_num', mysql.INTEGER(), server_default='0', nullable=False),
    sa.Column('wb_num', mysql.INTEGER(), server_default='0', nullable=False),
    sa.Column('level', mysql.INTEGER(), server_default='0', nullable=False),
    sa.Column('tags', mysql.TEXT(), nullable=True),
    sa.Column('work_info', sa.String(length=512), server_default='', nullable=False),
    sa.Column('contact_info', sa.String(length=512), server_default='', nullable=False),
    sa.Column('education_info', sa.String(length=512), server_default='', nullable=False),
    sa.Column('head_img', sa.String(length=512), server_default='', nullable=False),
    sa.PrimaryKeyConstraint('_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('robot_info_lib')
    # ### end Alembic commands ###