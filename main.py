import logging
import asyncio

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_sse import sse_response
from tortoise import ModelMeta
from tortoise.backends.asyncpg.client import TransactionWrapper
from tortoise.signals import Signals

from db.models import User, Ad
from db.user import user_upd_bc

logging.basicConfig(level=logging.DEBUG)


async def list_all(request: Request):
    data = []

    # noinspection PyUnusedLocal
    async def watchdog(meta: ModelMeta, ad: Ad, cr: bool, tw: TransactionWrapper, e):
        data.append(f"{ad.pair}: {ad.price}")

    Ad.register_listener(Signals.post_save, watchdog)

    async with sse_response(request) as resp:
        while resp.status == 200:
            if data:
                d = data.pop()
                await resp.send(d)
            else:
                await asyncio.sleep(1)


async def add_user(request: Request):
    data = await request.json()
    user: User = await user_upd_bc(**data)
    return web.json_response({'ok': user.uid})


app = web.Application()

app.add_routes([
    web.get("/", list_all),
    web.post("/user/bc", add_user)
])

if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    web.run_app(app, port=8000)
    pass
