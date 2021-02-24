import pytest

from app.game.answer.models import Answer
from app.game.question.models import Question


def answer2dict(answer: Answer):
    return {
        "question_id": answer.question_id,
        "title": answer.title,
        "is_right": answer.is_right,
    }


class TestAnswerCreateView:
    async def test_success(self, cli, question: Question):
        data = {"question_id": question.id, "title": "test", "is_right": False}
        response = await cli.post("/answer.create", json=data)
        assert response.status == 200
        answer = await Answer.query.gino.first()
        assert await response.json() == answer2dict(answer)


class TestAnswerUpdateView:
    async def test_success(self, cli, answer: Answer, question: Question):
        data = {"id": answer.id, "question_id": question.id, "title": "test1", "is_right": False}
        response = await cli.put("/answer.update", json=data)
        assert response.status == 200
        answer = await Answer.get(answer.id)
        assert await response.json() == answer2dict(answer)

    async def test_bad_id(self, cli, question: Question):
        data = {"id": 0, "question_id": question.id, "title": "test1", "is_right": False}
        response = await cli.put("/answer.update", json=data)
        assert response.status == 400
        assert await response.json() == {"code": "no_such_record"}


class TestAnswerDeleteView:
    async def test_success(self, cli, answer: Answer):
        data = {"id": answer.id}
        response = await cli.delete("/answer.delete", json=data)
        assert response.status == 204
        assert await response.json() == None

    async def test_bad_id(self, cli):
        data = {"id": 999}
        response = await cli.delete("/answer.delete", json=data)
        assert response.status == 400
        assert await response.json() == {"code": "no_such_record"}


class TestAnswerListView:
    @pytest.mark.parametrize(
        "params,expected_idxs",
        [
            [{}, [0, 1]],
            [{"limit": 1}, [0]],
            [{"offset": 1}, [1]],
            [{"title": "test1"}, [0]],
            [{"question_id": 999}, []],
        ],
    )
    async def test_success(
        self,
        cli,
        answers,
        params: dict,
        expected_idxs,
    ):
        response = await cli.get("/answer.list", params=params)
        assert response.status == 200
        assert await response.json() == [
            answer2dict(answers[idx]) for idx in expected_idxs
        ]
