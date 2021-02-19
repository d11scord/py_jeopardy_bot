from app.store.database.models import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer(), primary_key=True)
    theme = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(), nullable=False)
