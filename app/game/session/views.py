import random

from aiohttp import web
from aiohttp_apispec import (
    docs,
    json_schema,
    response_schema,
    querystring_schema,
)
from sqlalchemy import and_

from app.game.session.models import GameSession
from app.game.session.schemas import GameSessionSchema, GameSessionCreateSchema, GameSessionListSchema


class CreateGameSessionView(web.View):
    @docs(tags=["game"], summary="Create game session")
    @json_schema(GameSessionCreateSchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        questions = list(range(7))
        random.shuffle(questions)
        session = await GameSession.create(
            chat_id=self.request['json']["chat_id"],
            questions=questions,
            last_question_id=0,
            is_finished=False,
        )
        return web.json_response(GameSessionSchema().dump(session))


class GameSessionListView(web.View):
    @docs(tags=["game"], summary="Game sessions list")
    @querystring_schema(GameSessionListSchema)
    @response_schema(GameSessionSchema(many=True))
    async def get(self):
        data = self.request["querystring"]
        conditions = []
        # TODO: add user_id
        if data.get("chat_id"):
            conditions.append(GameSession.user_id == data["chat_id"])

        games = (
            await GameSession.load()
            .query.where(and_(*conditions))
            .order_by(GameSession.id)
            .limit(data["limit"])
            .offset(data["offset"])
            .gino.all()
        )
        return web.json_response(GameSessionSchema(many=True).dump(games))
