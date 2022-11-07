import asyncio

from tortoise import Tortoise
from tortoise.backends.asyncpg import AsyncpgDBClient
from tortoise.connection import connections

cns: [AsyncpgDBClient] = []
dsn = "postgres://artemiev:@/antifragility"


async def getin():
    await Tortoise.init(
        db_url=dsn,
        modules={"models": ["db.models"]},
        timezone="Europe/Moscow"
    )
    cns.append(*connections.all())

asyncio.run(getin())
