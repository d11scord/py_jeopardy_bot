import pytest

from app.game.user.models import User


@pytest.fixture
async def user():
    return await User.create(
        user_id=1,
        firstname="Имя",
        lastname="Фамилия",
        score=0,
    )


@pytest.fixture
async def users():
    await User.create(
        user_id=1,
        firstname="Имя",
        lastname="Фамилия",
        score=0,
    )
    await User.create(
        user_id=2,
        firstname="Имя",
        lastname="Фамилия",
        score=0,
    )
    return await User.load().query.gino.all()


