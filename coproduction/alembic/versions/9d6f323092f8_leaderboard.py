"""leaderboard

Revision ID: 9d6f323092f8
Revises: 990a22e75e5e
Create Date: 2023-09-12 09:15:11.343075

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d6f323092f8'
down_revision = '990a22e75e5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coproductionprocess', sa.Column('leaderboard', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coproductionprocess', 'leaderboard')
    # ### end Alembic commands ###
