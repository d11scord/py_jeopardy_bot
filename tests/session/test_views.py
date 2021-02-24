import pytest

from app.game.session.models import GameSession, SessionScores


def game2dict(game: GameSession):
    return {
        "chat_id": game.chat_id,
        "questions": game.questions,
        "last_question_id": game.last_question_id,
        "is_finished": game.is_finished,
    }


def session2dict(session: SessionScores):
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "score": session.score,
    }


class TestGameSessionCreateView:
    async def test_success(self, cli):
        data = {"chat_id": 12, "questions": [0, 1, 2]}
        response = await cli.post("/game.create", json=data)
        assert response.status == 200
        game = await GameSession.query.gino.first()
        assert await response.json() == game2dict(game)


class TestGameSessionDeleteView:
    async def test_success(self, cli, game_session: GameSession):
        data = {"id": game_session.id}
        response = await cli.delete("/game.delete", json=data)
        assert response.status == 204
        assert await response.json() == None

    async def test_bad_id(self, cli):
        data = {"id": 999}
        response = await cli.delete("/game.delete", json=data)
        assert response.status == 400
        assert await response.json() == {"code": "no_such_record"}


class TestGameSessionListView:
    @pytest.mark.parametrize(
        "params,expected_idxs",
        [
            [{}, [0, 1]],
            [{"limit": 1}, [0]],
            [{"offset": 1}, [1]],
            [{"chat_id": 2}, [1]],
        ],
    )
    async def test_success(
        self,
        cli,
        game_sessions,
        params: dict,
        expected_idxs,
    ):
        response = await cli.get("/game.list", params=params)
        assert response.status == 200
        assert await response.json() == [
            game2dict(game_sessions[idx]) for idx in expected_idxs
        ]


class TestSessionScoresListView:
    @pytest.mark.parametrize(
        "params,expected_idxs",
        [
            [{}, [0, 1]],
            [{"limit": 1}, [0]],
            [{"offset": 1}, [1]],
        ],
    )
    async def test_success(
        self,
        cli,
        session_scores,
        params: dict,
        expected_idxs,
    ):
        response = await cli.get("/session.list", params=params)
        assert response.status == 200
        assert await response.json() == [
            session2dict(session_scores[idx]) for idx in expected_idxs
        ]
