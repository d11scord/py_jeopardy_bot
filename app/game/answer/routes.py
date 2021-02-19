from aiohttp import web

from app.game.answer.views import (
    CreateAnswerView,
    DeleteAnswerView,
    AnswerListView,
)


def setup_routes(app: web.Application) -> None:
    app.router.add_view("/answer.create", CreateAnswerView)
    app.router.add_view("/answer.delete", DeleteAnswerView)
    app.router.add_view("/answer.list", AnswerListView)
