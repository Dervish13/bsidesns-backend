"""blog

Revision ID: 390f37ec4c5c
Revises: 4dd102097d35
Create Date: 2021-11-01 22:08:49.256566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '390f37ec4c5c'
down_revision = '4dd102097d35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blogs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.CHAR(36), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('published', sa.Boolean(), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author'], ['users.id'], name='fk_blogs_users_id_author'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blogs')
    # ### end Alembic commands ###
