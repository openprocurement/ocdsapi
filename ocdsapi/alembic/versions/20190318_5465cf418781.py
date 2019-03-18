"""indexes

Revision ID: 5465cf418781
Revises: 111b3500ad0b
Create Date: 2019-03-18 13:07:52.408426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5465cf418781'
down_revision = '111b3500ad0b'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('record-timestamp-id', 'records', [sa.text('timestamp ASC'), 'id'], unique=False)
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('record-timestamp-id', table_name='records')
    # ### end Alembic commands ###
