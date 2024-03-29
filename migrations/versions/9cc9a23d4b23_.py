"""empty message

Revision ID: 9cc9a23d4b23
Revises: a3ebb8855567
Create Date: 2019-06-17 16:32:00.560865

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9cc9a23d4b23'
down_revision = 'a3ebb8855567'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('application', 'active',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('application', 'id',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=40), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('application', 'id',
               existing_type=sa.String(length=40),
               type_=mysql.VARCHAR(length=20))
    op.alter_column('application', 'active',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    # ### end Alembic commands ###
