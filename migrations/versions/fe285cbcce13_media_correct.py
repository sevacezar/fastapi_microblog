"""media_correct

Revision ID: fe285cbcce13
Revises: 93e5d4a8a950
Create Date: 2024-06-24 12:01:51.968656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe285cbcce13'
down_revision: Union[str, None] = '93e5d4a8a950'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medias', sa.Column('name', sa.String(), nullable=False))
    op.drop_constraint('medias_tweet_id_fkey', 'medias', type_='foreignkey')
    op.drop_column('medias', 'link')
    op.drop_column('medias', 'tweet_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medias', sa.Column('tweet_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('medias', sa.Column('link', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_foreign_key('medias_tweet_id_fkey', 'medias', 'tweets', ['tweet_id'], ['id'])
    op.drop_column('medias', 'name')
    # ### end Alembic commands ###
