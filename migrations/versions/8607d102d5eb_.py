"""empty message

Revision ID: 8607d102d5eb
Revises: 0eff9fa23f1a
Create Date: 2024-05-03 22:18:47.595765

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8607d102d5eb'
down_revision = '0eff9fa23f1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('follow', schema=None) as batch_op:
        batch_op.drop_constraint('follow_follow_username_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('follow', schema=None) as batch_op:
        batch_op.create_unique_constraint('follow_follow_username_key', ['follow_username'])

    # ### end Alembic commands ###
