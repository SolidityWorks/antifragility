# import logging
from aiohttp import web
from tortoise.contrib.aiohttp import register_tortoise

from loader import orm_params
from models import User

# logging.basicConfig(level=logging.DEBUG)


async def list_all(request):
    users = await User.all()
    return web.json_response({"users": [str(user) for user in users]})


async def add_user(request):
    user = await User.create(name="New User")
    return web.json_response({"user": str(user)})


app = web.Application()
register_tortoise(app, **orm_params)

app.add_routes([
    web.get("/", list_all),
    web.post("/user", add_user)
])

if __name__ == "__main__":
    web.run_app(app)
