"""update operational activities model

Revision ID: 22da14b90768
Revises: 15cfd3f5e37d
Create Date: 2019-02-21 18:07:35.088987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22da14b90768'
down_revision = '15cfd3f5e37d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('operational_activities', sa.Column('amount', sa.Numeric(precision=16, scale=2), server_default='0.00', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('operational_activities', 'amount')
    # ### end Alembic commands ###
