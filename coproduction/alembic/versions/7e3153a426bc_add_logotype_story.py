"""add_logotype_story

Revision ID: 7e3153a426bc
Revises: 1e7f299eebb8
Create Date: 2023-04-25 14:12:57.220276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e3153a426bc'
down_revision = '1e7f299eebb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('story', sa.Column('logotype', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('story', 'logotype')
    # ### end Alembic commands ###
