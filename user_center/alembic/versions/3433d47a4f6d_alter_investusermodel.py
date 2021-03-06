"""alter investusermodel

Revision ID: 3433d47a4f6d
Revises: ff76479864bf
Create Date: 2018-10-31 16:13:51.786062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3433d47a4f6d'
down_revision = 'ff76479864bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invest_users', sa.Column('transaction_bcrypt_salt', sa.String(length=128), server_default='', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invest_users', 'transaction_bcrypt_salt')
    # ### end Alembic commands ###
