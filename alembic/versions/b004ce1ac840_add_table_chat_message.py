"""Add table chat_message

Revision ID: b004ce1ac840
Revises: 
Create Date: 2021-01-25 11:48:58.511513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b004ce1ac840'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nickname', sa.String(length=50), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_message')
    # ### end Alembic commands ###
