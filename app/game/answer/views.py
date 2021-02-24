from aiohttp import web
from aiohttp_apispec import docs, querystring_schema, response_schema, json_schema
from sqlalchemy import and_

from app.game.answer.models import Answer
from app.game.answer.schemas import (
    AnswerSchema,
    AnswerCreateSchema,
    AnswerUpdateSchema,
    AnswerDeleteSchema,
    AnswerListSchema,
)


class CreateAnswerView(web.View):
    @docs(tags=["answer"], summary="Create answer")
    @json_schema(AnswerCreateSchema)
    @response_schema(AnswerSchema)
    async def post(self):
        answer = await Answer.create(
            question_id=self.request['json']["question_id"],
            title=self.request['json']["title"],
            is_right=self.request['json']["is_right"],
        )
        return web.json_response(AnswerSchema().dump(answer))


class UpdateAnswerView(web.View):
    @docs(tags=["answer"], summary="Update answer")
    @json_schema(AnswerUpdateSchema)
    @response_schema(AnswerSchema)
    async def put(self):
        answer = await Answer.get(self.request['json']["id"])
        await answer.update(
            question_id=self.request['json']["question_id"],
            title=self.request['json']["title"],
            is_right=self.request['json']["is_right"],
        ).apply()
        return web.json_response(AnswerSchema().dump(answer))


class DeleteAnswerView(web.View):
    @docs(tags=["answer"], summary="Delete answer")
    @json_schema(AnswerDeleteSchema)
    async def delete(self):
        await (
            Answer.delete
            .where(Answer.id == self.request['json']["id"])
            .gino.status()
        )
        return web.json_response({}, status=204)


class AnswerListView(web.View):
    @docs(tags=["answer"], summary="Answers list")
    @querystring_schema(AnswerListSchema)
    @response_schema(AnswerSchema(many=True))
    async def get(self):
        data = self.request["querystring"]
        conditions = []
        if data.get("question_id"):
            conditions.append(Answer.question_id == data["question_id"])
        if data.get("title"):
            conditions.append(Answer.title.contains(data["title"]))

        answers = (
            await Answer.load()
            .query.where(and_(*conditions))
            .order_by(Answer.id)
            .limit(data["limit"])
            .offset(data["offset"])
            .gino.all()
        )
        return web.json_response(AnswerSchema(many=True).dump(answers))
