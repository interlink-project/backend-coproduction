"""addingTypeclaimtable

Revision ID: 794605c8228b
Revises: 432b4d79a2b5
Create Date: 2023-07-04 11:13:10.131704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '794605c8228b'
down_revision = '432b4d79a2b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('claim', sa.Column('claim_type', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('claim', 'claim_type')
    # ### end Alembic commands ###
