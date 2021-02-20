"""add on_delete session_scores 1

Revision ID: 35d8d8ecf830
Revises: 2f75d03d163e
Create Date: 2021-02-20 22:40:57.618203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35d8d8ecf830'
down_revision = '2f75d03d163e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('session_scores_session_id_fkey', 'session_scores', type_='foreignkey')
    op.drop_constraint('session_scores_user_id_fkey', 'session_scores', type_='foreignkey')
    op.create_foreign_key(None, 'session_scores', 'game_sessions', ['session_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'session_scores', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'session_scores', type_='foreignkey')
    op.drop_constraint(None, 'session_scores', type_='foreignkey')
    op.create_foreign_key('session_scores_user_id_fkey', 'session_scores', 'users', ['user_id'], ['user_id'])
    op.create_foreign_key('session_scores_session_id_fkey', 'session_scores', 'game_sessions', ['session_id'], ['id'])
    # ### end Alembic commands ###
