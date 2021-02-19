from aiohttp import web

from app.game.user.views import UserListView


def setup_routes(app: web.Application) -> None:
    app.router.add_view("/user.list", UserListView)
