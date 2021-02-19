from app.store.database.models import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    score = db.Column(db.Integer(), nullable=False)
