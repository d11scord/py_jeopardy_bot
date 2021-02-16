import asyncio

from aiohttp import web
from aiojobs.aiohttp import setup

from app.settings import config
from app.vk_async.accessor import VkAccessor


def setup_config(application: web.Application) -> None:
    application["config"] = config


def setup_accessors(application: web.Application) -> None:
    VkAccessor().setup(application)


def setup_app(application: web.Application) -> None:
    setup_config(application)
    setup_accessors(application)

    app.on_startup.append(start_background_tasks)


async def start_background_tasks(app):
    # https://docs.aiohttp.org/en/v3.7.3/web_advanced.html#background-tasks
    app['vk_listener'] = asyncio.create_task(app['vk'].listen_to_messages())


async def cleanup_background_tasks(app):
    app['vk'].cancel()
    await app['vk']


app = web.Application()
setup(app)

if __name__ == "__main__":
    setup_app(app)
    print('Run app')
    web.run_app(app, port=config["common"]["port"])
