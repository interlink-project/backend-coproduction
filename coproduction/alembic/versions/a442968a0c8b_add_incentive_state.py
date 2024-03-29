"""add_incentive_state

Revision ID: a442968a0c8b
Revises: 7bbdc4cbbdb5
Create Date: 2023-02-08 12:36:52.130894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a442968a0c8b'
down_revision = '7bbdc4cbbdb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coproductionprocess', sa.Column('incentive_and_rewards_state', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coproductionprocess', 'incentive_and_rewards_state')
    # ### end Alembic commands ###
