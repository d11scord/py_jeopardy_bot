import asyncio

from aiohttp import web

from app.settings import config
from app.vk.accessor import VkAccessor


def setup_config(application: web.Application) -> None:
    application["config"] = config


# def setup_routes(application: web.Application) -> None:
#     from app.vk.routes import setup_routes
#
#     setup_routes(application)


def setup_accessors(application: web.Application) -> None:
    VkAccessor().setup(application)


def setup_app(application: web.Application) -> None:
    setup_config(application)
    # setup_routes(application)
    setup_accessors(application)

    application.on_startup.append(start_background_tasks)
    application.on_cleanup.append(cleanup_background_tasks)


async def start_background_tasks(app):
    print('Creating vk task')
    app['vk_listener'] = asyncio.create_task(app['vk'].listen_to_messages())


async def cleanup_background_tasks(app):
    print('Stopping vk task')
    app['vk_listener'].cancel()
    await app['vk_listener']


app = web.Application()

if __name__ == "__main__":
    setup_app(app)
    print('Run app')
    web.run_app(app, port=config["common"]["port"])
