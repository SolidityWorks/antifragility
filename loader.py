import asyncio

from tortoise import Tortoise
from tortoise.backends.asyncpg import AsyncpgDBClient
from tortoise.connection import connections
from dotenv import load_dotenv
from os import getenv as env

load_dotenv()
cns: [AsyncpgDBClient] = []
dsn = env('PG_DSN')


async def getin():
    await Tortoise.init(
        db_url=dsn,
        modules={"models": ["db.models"]},
        timezone="Europe/Moscow"
    )
    cns.append(*connections.all())

asyncio.run(getin())
