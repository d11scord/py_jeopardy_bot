import pytest

from app.game.user.models import User


def user2dict(user: User):
    return {
        "user_id": user.user_id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "score": user.score,
    }


class TestUserListView:
    @pytest.mark.parametrize(
        "params,expected_idxs",
        [
            [{}, [0, 1]],
            [{"limit": 1}, [0]],
            [{"offset": 1}, [1]],
        ],
    )
    async def test_user_list(
        self,
        cli,
        users,
        params: dict,
        expected_idxs,
    ):
        response = await cli.get("/user.list", params=params)
        assert response.status == 200
        assert await response.json() == [
            user2dict(users[idx]) for idx in expected_idxs
        ]
