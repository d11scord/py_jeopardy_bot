import pytest

from app.game.session.models import GameSession, SessionScores
from app.game.user.models import User


@pytest.fixture
async def game_session():
    return await GameSession.create(
        chat_id=999,
        questions=[0, 1, 2],
        last_question_id=0,
        is_finished=False,
    )


@pytest.fixture
async def game_sessions():
    await GameSession.create(
        chat_id=1,
        questions=[0, 1, 2],
        last_question_id=0,
        is_finished=False,
    )
    await GameSession.create(
        chat_id=2,
        questions=[0, 1, 2],
        last_question_id=2,
        is_finished=True,
    )
    return await GameSession.load().query.gino.all()


@pytest.fixture
async def session_scores(game_session: GameSession, user: User):
    await SessionScores.create(
        session_id=game_session.id,
        user_id=user.user_id,
        score=0,
    )
    await SessionScores.create(
        session_id=game_session.id,
        user_id=user.user_id,
        score=100,
    )
    return await SessionScores.load().query.gino.all()
