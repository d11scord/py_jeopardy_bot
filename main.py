import logging

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

from app.settings import config
from app.store.database.models import database_accessor


def setup_config(application: web.Application) -> None:
    application["config"] = config


def setup_accessors(application: web.Application) -> None:
    database_accessor.setup(application)


def setup_middlewares(application: web.Application) -> None:
    application.middlewares.append(validation_middleware)


def setup_routes(application: web.Application) -> None:
    from app.game.session.routes import setup_routes as setup_game_routes
    from app.game.user.routes import setup_routes as setup_user_routes
    from app.game.question.routes import setup_routes as setup_question_routes
    from app.game.answer.routes import setup_routes as setup_answer_routes

    setup_game_routes(application)
    setup_user_routes(application)
    setup_question_routes(application)
    setup_answer_routes(application)


def setup_external_libraries(application: web.Application) -> None:
    setup_aiohttp_apispec(
        app=application,
        title="Своя игра бот. Документация",
        version="v1",
        url="/swagger.json",
        swagger_path="/swagger",
    )


def setup_logging(_: web.Application) -> None:
    logging.basicConfig(level=logging.INFO)


def setup_app(application: web.Application) -> None:
    setup_config(application)
    setup_accessors(application)
    setup_middlewares(application)
    setup_routes(application)
    setup_external_libraries(application)
    # setup_logging(application)


app = web.Application()

if __name__ == "__main__":
    setup_app(app)
    print('Run app')
    web.run_app(app, port=config["common"]["port"])
