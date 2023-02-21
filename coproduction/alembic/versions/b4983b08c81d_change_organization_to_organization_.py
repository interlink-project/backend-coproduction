"""change_organization_to_organization_desc_in_coproductionprocess

Revision ID: b4983b08c81d
Revises: 86b8b82d8317
Create Date: 2023-01-25 10:51:06.120533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4983b08c81d'
down_revision = '270a1c42c6fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coproductionprocess', sa.Column('organization_desc', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coproductionprocess', 'organization_desc')
    # ### end Alembic commands ###