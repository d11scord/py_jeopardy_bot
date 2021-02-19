from aiohttp import web
from aiohttp_apispec import docs, querystring_schema, response_schema, json_schema
from sqlalchemy import and_

from app.game.question.models import Question
from app.game.question.schemas import (
    QuestionSchema,
    QuestionListSchema,
    QuestionCreateSchema,
    QuestionDeleteSchema,
)


class CreateQuestionView(web.View):
    @docs(tags=["question"], summary="Create question")
    @json_schema(QuestionCreateSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        question = await Question.create(
            theme=self.request['json']["theme"],
            title=self.request['json']["title"],
        )
        return web.json_response(QuestionSchema().dump(question))


class DeleteQuestionView(web.View):
    @docs(tags=["question"], summary="Delete question")
    @json_schema(QuestionDeleteSchema)
    async def delete(self):
        _ = await (
            Question.delete
            .where(Question.id == self.request['json']["id"])
            .gino.status()
        )
        return web.json_response({}, status=204)


class QuestionListView(web.View):
    @docs(tags=["question"], summary="Questions list")
    @querystring_schema(QuestionListSchema)
    @response_schema(QuestionSchema(many=True))
    async def get(self):
        data = self.request["querystring"]
        conditions = []
        if data.get("theme"):
            conditions.append(Question.theme.contains(data["theme"]))

        questions = (
            await Question.load()
            .query.where(and_(*conditions))
            .order_by(Question.id)
            .limit(data["limit"])
            .offset(data["offset"])
            .gino.all()
        )
        return web.json_response(QuestionSchema(many=True).dump(questions))
