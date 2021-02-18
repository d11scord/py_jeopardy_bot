from aiohttp import web

from app.settings import config
from app.vk.accessor import VkAccessor
from app.vk.longpoll import LongPoll


def setup_config(application: web.Application) -> None:
    application["config"] = config


def setup_accessors(application: web.Application) -> None:
    VkAccessor().setup(application)
    LongPoll().setup(application)


def setup_app(application: web.Application) -> None:
    setup_config(application)
    setup_accessors(application)


app = web.Application()

if __name__ == "__main__":
    setup_app(app)
    print('Run app')
    web.run_app(app, port=config["common"]["port"])
