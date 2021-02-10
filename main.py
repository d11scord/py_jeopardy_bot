from aiohttp import web

from app.settings import config
from app.vk.accessor import VkAccessor


def setup_config(application: web.Application) -> None:
    application["config"] = config


def setup_routes(application: web.Application) -> None:
    from app.vk.routes import setup_routes

    setup_routes(application)


def setup_accessors(application: web.Application) -> None:
    VkAccessor().setup(application)


def setup_app(application: web.Application) -> None:
    setup_config(application)
    setup_routes(application)
    setup_accessors(application)


app = web.Application()

if __name__ == "__main__":
    setup_app(app)
    web.run_app(app, port=config["common"]["port"])
