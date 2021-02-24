from aiohttp import web

from app.game.question.views import (
    CreateQuestionView,
    UpdateQuestionView,
    DeleteQuestionView,
    QuestionListView,
)


def setup_routes(app: web.Application) -> None:
    app.router.add_view("/question.create", CreateQuestionView)
    app.router.add_view("/question.update", UpdateQuestionView)
    app.router.add_view("/question.delete", DeleteQuestionView)
    app.router.add_view("/question.list", QuestionListView)
