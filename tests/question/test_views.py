import pytest

from app.game.question.models import Question


def question2dict(question: Question):
    return {
        "theme": question.theme,
        "title": question.title,
        "id": question.id,
    }


class TestQuestionCreateView:
    async def test_success(self, cli):
        data = {"theme": "test", "title": "test"}
        response = await cli.post("/question.create", json=data)
        assert response.status == 200
        question = await Question.query.gino.first()
        assert await response.json() == question2dict(question)


class TestQuestionUpdateView:
    async def test_success(self, cli, question: Question):
        data = {"id": question.id, "theme": "test1", "title": "test1"}
        response = await cli.put("/question.update", json=data)
        assert response.status == 200
        question = await Question.get(question.id)
        assert await response.json() == question2dict(question)

    async def test_bad_id(self, cli):
        data = {"id": 0, "theme": "test1", "title": "test1"}
        response = await cli.put("/question.update", json=data)
        assert response.status == 400
        assert await response.json() == {"code": "no_such_record"}


class TestQuestionDeleteView:
    async def test_success(self, cli, question: Question):
        data = {"id": question.id}
        response = await cli.delete("/question.delete", json=data)
        assert response.status == 204
        assert await response.json() == None

    async def test_bad_id(self, cli):
        data = {"id": 999}
        response = await cli.delete("/question.delete", json=data)
        assert response.status == 400
        assert await response.json() == {"code": "no_such_record"}


class TestQuestionListView:
    @pytest.mark.parametrize(
        "params,expected_idxs",
        [
            [{}, [0, 1]],
            [{"limit": 1}, [0]],
            [{"offset": 1}, [1]],
            [{"theme": "Тема вопроса 1"}, [0]],
        ],
    )
    async def test_success(
        self,
        cli,
        questions,
        params: dict,
        expected_idxs,
    ):
        response = await cli.get("/question.list", params=params)
        assert response.status == 200
        assert await response.json() == [
            question2dict(questions[idx]) for idx in expected_idxs
        ]
