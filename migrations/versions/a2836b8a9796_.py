"""empty message

Revision ID: a2836b8a9796
Revises: 199092c2dcad
Create Date: 2022-06-25 18:17:30.974443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2836b8a9796'
down_revision = '199092c2dcad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_message_notification_time', sa.DateTime(), nullable=True))
    op.drop_column('user', 'last_message_read_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_message_read_time', sa.DATETIME(), nullable=True))
    op.drop_column('user', 'last_message_notification_time')
    # ### end Alembic commands ###