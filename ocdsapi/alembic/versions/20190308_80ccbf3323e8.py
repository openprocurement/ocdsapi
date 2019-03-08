"""simpler ids

Revision ID: 80ccbf3323e8
Revises: 83318be22486
Create Date: 2019-03-08 17:17:33.540370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80ccbf3323e8'
down_revision = '83318be22486'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('releases', 'release_id', new_column_name='id')
    # op.add_column('releases', sa.Column('id', sa.String(), nullable=False))
    # op.drop_column('releases', 'release_id')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('releases', 'id', new_column_name='release_id')
    # op.add_column('releases', sa.Column('release_id', sa.VARCHAR(), autoincrement=False, nullable=False))
    # op.drop_column('releases', 'id')
    # # ### end Alembic commands ###
