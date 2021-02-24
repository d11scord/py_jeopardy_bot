import functools

from gino import GinoEngine

from app import settings

settings.config = settings.get_config(
    settings.BASE_DIR / "config" / "tests.yaml"
)

from main import create_app
from tests.fixtures import *


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def cli(aiohttp_client, app):
    client = await aiohttp_client(app)
    yield client


@pytest.fixture(autouse=True)
async def db_transaction(cli):

    db = cli.app["db"].db
    real_acquire = GinoEngine.acquire

    async with db.acquire() as conn:

        class _AcquireContext:
            __slots__ = ["_acquire", "_conn"]

            def __init__(self, acquire):
                self._acquire = acquire

            async def __aenter__(self):
                return conn

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            def __await__(self):
                return conn

        def acquire(
            self, *, timeout=None, reuse=False, lazy=False, reusable=True
        ):
            return _AcquireContext(
                functools.partial(self._acquire, timeout, reuse, lazy, reusable)
            )

        GinoEngine.acquire = acquire
        transaction = await conn.transaction()
        yield
        await transaction.rollback()
        GinoEngine.acquire = real_acquire
