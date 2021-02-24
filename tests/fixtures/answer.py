import pytest

from app.game.answer.models import Answer
from app.game.question.models import Question


@pytest.fixture
async def answer(question: Question):
    return await Answer.create(
        question_id=question.id,
        title="test",
        is_right=False,
    )


@pytest.fixture
async def answers(question: Question):
    await Answer.create(
        question_id=question.id,
        title="test1",
        is_right=False,
    )
    await Answer.create(
        question_id=question.id,
        title="test2",
        is_right=True,
    )
    return await Answer.load().query.gino.all()
