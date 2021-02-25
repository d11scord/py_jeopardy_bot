import logging
from argparse import ArgumentParser

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

from app.base.base import error_middleware
from app.settings import config
from app.store.database.models import database_accessor
from app.vk.longpoll import run_longpoll
from app.worker.worker import run_worker


def setup_config(application: web.Application) -> None:
    application["config"] = config


def setup_accessors(application: web.Application) -> None:
    database_accessor.setup(application)


def setup_middlewares(application: web.Application) -> None:
    application.middlewares.append(error_middleware)
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
        swagger_path="/",
    )


def setup_logging(_: web.Application) -> None:
    logging.basicConfig(level=logging.INFO)


def create_app() -> web.Application:
    application = web.Application()

    setup_config(application)
    setup_accessors(application)
    setup_middlewares(application)
    setup_routes(application)
    setup_external_libraries(application)
    setup_logging(application)

    return application


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="specify running service")
    arg_parser.add_argument(
        "service", help="web or worker or longpoll", default="web", type=str
    )
    args = arg_parser.parse_args()
    if args.service == "worker":
        run_worker()
    elif args.service == "longpoll":
        run_longpoll()
    else:
        app = create_app()
        web.run_app(app, port=config["common"]["port"])
