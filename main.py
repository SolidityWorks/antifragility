# import logging
from aiohttp import web
from aiohttp.web_request import Request
from tortoise.contrib.aiohttp import register_tortoise

from db.update import user_upd_bc
from loader import orm_params
from db.models import User

# logging.basicConfig(level=logging.DEBUG)


async def list_all(request):
    users = await User.all()
    return web.json_response({"users": [str(user) for user in users]})


async def add_user(request: Request):
    data = await request.json()
    user: User = await user_upd_bc(**data)
    return web.json_response({'ok': user.uid})


app = web.Application()
register_tortoise(app, **orm_params)

app.add_routes([
    web.get("/", list_all),
    web.post("/user/bc", add_user)
])

if __name__ == "__main__":
    web.run_app(app, port=8000)
