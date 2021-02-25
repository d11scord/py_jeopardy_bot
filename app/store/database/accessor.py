import ssl

from aiohttp import web
from sqlalchemy.engine.url import URL

from app.settings import config


class PostgresAccessor:
    def __init__(self) -> None:

        self.db = None

    def setup(self, application: web.Application) -> None:
        application.on_startup.append(self._on_connect)
        application.on_cleanup.append(self._on_disconnect)

    async def _on_connect(self, application: web.Application):
        from app.store.database.models import db

        self.db = db
        await self.db.set_bind(
            URL(
                drivername="asyncpg",
                username=config["database"]["username"],
                password=config["database"]["password"],
                host=config["database"]["host"],
                port=config["database"]["port"],
                database=config["database"]["name"],
            ),
            min_size=1,
            max_size=1,
        )

        application["db"] = self

    async def _on_disconnect(self, _) -> None:
        if self.db is not None:
            await self.db.pop_bind().close()
