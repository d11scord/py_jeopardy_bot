import pytest

from app.game.question.models import Question


@pytest.fixture
async def question():
    return await Question.create(theme="Тема вопроса 1", title="Вопрос 1?")


@pytest.fixture
async def questions():
    await Question.create(theme="Тема вопроса 1", title="Вопрос 1?")
    await Question.create(theme="Тема вопроса 2", title="Вопрос 2?")
    return await Question.load().query.gino.all()
