"""empty message

Revision ID: 086d624bd22c
Revises: 87e930cacf8f
Create Date: 2024-01-30 13:28:00.777113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '086d624bd22c'
down_revision = '87e930cacf8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_genres',
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    info={'bind_key': None}
    )
    op.create_table('venue_genres',
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    info={'bind_key': None}
    )
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('genres')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))

    op.drop_table('venue_genres')
    op.drop_table('artist_genres')
    op.drop_table('Genre')
    # ### end Alembic commands ###
