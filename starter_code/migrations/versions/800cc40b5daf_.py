"""empty message

Revision ID: 800cc40b5daf
Revises: fcb882eeda78
Create Date: 2021-02-11 12:52:50.273962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '800cc40b5daf'
down_revision = 'fcb882eeda78'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.drop_column('artists', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('artists', 'seeking_venue')
    # ### end Alembic commands ###
