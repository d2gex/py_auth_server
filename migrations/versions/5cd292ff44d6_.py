"""empty message

Revision ID: 5cd292ff44d6
Revises: ad3dd310f9c5
Create Date: 2019-06-18 08:14:58.991644

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5cd292ff44d6'
down_revision = 'ad3dd310f9c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('application', 'active',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.create_unique_constraint(None, 'application', ['reg_token'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'application', type_='unique')
    op.alter_column('application', 'active',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    # ### end Alembic commands ###
