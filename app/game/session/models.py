from sqlalchemy.dialects.postgresql import ARRAY

from app.store.database.models import db


class GameSession(db.Model):
    __tablename__ = "game_sessions"

    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), nullable=False)
    questions = db.Column(ARRAY(db.Integer()), nullable=False)
    last_question_id = db.Column(db.Integer(), nullable=False)
    is_finished = db.Column(db.Boolean(), nullable=False)



