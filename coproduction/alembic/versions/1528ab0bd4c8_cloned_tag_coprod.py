"""cloned_tag_coprod

Revision ID: 1528ab0bd4c8
Revises: 208738f13dce
Create Date: 2023-05-19 12:20:22.111430

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1528ab0bd4c8'
down_revision = '208738f13dce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coproductionprocess', sa.Column('cloned_from_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_copro_id_cloned_from', 'coproductionprocess', 'coproductionprocess', ['cloned_from_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_copro_id_cloned_from', 'coproductionprocess', type_='foreignkey')
    op.drop_column('coproductionprocess', 'cloned_from_id')
    # ### end Alembic commands ###
