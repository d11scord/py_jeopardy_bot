from aiohttp import web
from aiohttp_apispec import docs, querystring_schema, response_schema

from app.game.user.models import User
from app.game.user.schemas import UserSchema, UserListSchema


class UserListView(web.View):
    @docs(tags=["user"], summary="User list")
    @querystring_schema(UserListSchema)
    @response_schema(UserSchema(many=True))
    async def get(self):
        data = self.request["querystring"]

        users = (
            await User.load()
            .order_by(User.user_id)
            .limit(data["limit"])
            .offset(data["offset"])
            .gino.all()
        )
        return web.json_response(UserSchema(many=True).dump(users))
