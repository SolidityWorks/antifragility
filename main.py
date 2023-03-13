import json
import logging
from asyncio import sleep

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_sse import sse_response
from asyncpg import Connection, connect

from db.models import User, Pair
from db.user import user_upd_bc

logging.basicConfig(level=logging.DEBUG)


async def sse(request: Request):
    coins = request.match_info.get('coins', '').split(',')
    curs = request.match_info.get('curs', '').split(',')
    pq = Pair
    if coins != ['all']:
        pq = pq.filter(coin_id__in=coins)
    if curs != ['all']:
        pq = pq.filter(cur_id__in=curs)
    pairs = await pq.all().prefetch_related('ads')
    prs = [p.id for p in pairs]
    data = {pair.id: [{"x": int(ad.updated_at.timestamp()*1000), "y": ad.price} for ad in pair.ads.related_objects] for pair in pairs}

    # noinspection PyUnusedLocal
    async def watchdog(cn: Connection, pid: int, channel: str, payload: str):
        ad = json.loads(payload)
        if ad['pair_id'] in prs:
            data.get(ad['pair_id'], []).append({"x": int(ad['updated_at'].timestamp()*1000), "y": ad['price']})

    conn: Connection = await connect(dsn)
    await conn.add_listener('pc', watchdog)

    async with sse_response(request, headers={'Access-Control-Allow-Origin': '*'}) as resp:
        while resp.status == 200:
            [await resp.send(json.dumps({pid: ads.pop()})) for pid, ads in data.items() if ads]
            await sleep(1)


async def add_user(request: Request):
    data = await request.json()
    user: User = await user_upd_bc(**data)
    return web.json_response({'ok': user.uid})


app = web.Application()

app.add_routes([
    web.get("/sse", sse),
    web.get("/ssf/{coins}/{curs}", sse),
    web.post("/user/bc", add_user)
])

if __name__ == "__main__":
    from loader import dsn
    web.run_app(app, port=8008)
    pass
