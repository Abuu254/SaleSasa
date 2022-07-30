"""empty message

Revision ID: 22c224d53cd9
Revises: a2836b8a9796
Create Date: 2022-06-25 18:54:34.881034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22c224d53cd9'
down_revision = 'a2836b8a9796'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('unread', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'unread')
    # ### end Alembic commands ###
