"""drop title tests

Revision ID: bb67223f70bf
Revises: 46e2372472a3
Create Date: 2021-02-20 18:13:43.447263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb67223f70bf'
down_revision = '46e2372472a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answers',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=45), autoincrement=False, nullable=False),
    sa.Column('is_right', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('tests', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name='answers_question_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='answers_pkey')
    )
    # ### end Alembic commands ###
