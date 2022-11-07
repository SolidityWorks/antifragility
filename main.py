import json
import logging
import asyncio
from time import time

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_sse import sse_response
from asyncpg import Connection, connect

from db.models import User
from db.user import user_upd_bc

logging.basicConfig(level=logging.DEBUG)


async def sse(request: Request):
    data = []
    pairs = request.match_info.get('pair_id', '').split(',')

    # noinspection PyUnusedLocal
    async def watchdog(cn: Connection, pid: int, channel: str, payload: str):
        ad = json.loads(payload)
        if str(ad['pair_id']) in pairs or not pairs[0]:
            data.append(json.dumps({ad['pair_id']: {"x": time()*1000, "y": ad['price']}}))

    conn: Connection = await connect(dsn)
    await conn.add_listener('pc', watchdog)

    async with sse_response(request, headers={'Access-Control-Allow-Origin': '*'}) as resp:
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
    web.get("/sse", sse),
    web.get("/ssf/{pair_id}", sse),
    web.post("/user/bc", add_user)
])

if __name__ == "__main__":
    from loader import dsn
    web.run_app(app, port=8000)
    pass
