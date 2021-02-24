from aiohttp import web

from app.game.session.views import (
    CreateGameSessionView,
    GameSessionListView,
    DeleteGameSessionView,
    SessionScoresListView,
)


def setup_routes(app: web.Application) -> None:
    app.router.add_view("/game.create", CreateGameSessionView)
    app.router.add_view("/game.delete", DeleteGameSessionView)
    app.router.add_view("/game.list", GameSessionListView)
    app.router.add_view("/session.list", SessionScoresListView)
