from app.store.database.models import db


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer(), primary_key=True)
    question_id = db.Column(db.Integer(), db.ForeignKey("questions.id"), nullable=False)
    title = db.Column(db.String(45), nullable=False)
    is_right = db.Column(db.Boolean(), nullable=False)
