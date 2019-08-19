"""alter adminusermodel

Revision ID: 097992af7dc6
Revises: badd50650295
Create Date: 2018-09-03 17:22:27.063082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '097992af7dc6'
down_revision = 'badd50650295'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin_users', sa.Column('user_id', sa.String(length=64), server_default='', nullable=False))
    op.create_unique_constraint(None, 'admin_users', ['user_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'admin_users', type_='unique')
    op.drop_column('admin_users', 'user_id')
    # ### end Alembic commands ###