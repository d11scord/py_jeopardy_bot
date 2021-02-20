from gino import Gino

from app.store.database.accessor import PostgresAccessor

db = Gino()
# Все модели должны быть в памяти при миграциях,
# поэтому здесь инстанцируется аксессор, в котором они импортированы
database_accessor = PostgresAccessor()

from app.game.session.models import GameSession, SessionScores
from app.game.user.models import User
from app.game.question.models import Question
from app.game.answer.models import Answer
