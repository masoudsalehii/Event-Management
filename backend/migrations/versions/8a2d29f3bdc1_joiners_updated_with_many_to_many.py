"""joiners updated with many to many

Revision ID: 8a2d29f3bdc1
Revises: 1be0a11d26e2
Create Date: 2024-10-12 17:25:18.556094

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8a2d29f3bdc1'
down_revision = '1be0a11d26e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('joiners')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('joiners', mysql.VARCHAR(length=100), nullable=True))

    # ### end Alembic commands ###
