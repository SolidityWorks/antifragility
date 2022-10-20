# import logging
from aiohttp import web
from tortoise.contrib.aiohttp import register_tortoise

from models import User

# logging.basicConfig(level=logging.DEBUG)


async def list_all(request):
    users = await User.all()
    return web.json_response({"users": [str(user) for user in users]})


async def add_user(request):
    user = await User.create(name="New User")
    return web.json_response({"user": str(user)})


app = web.Application()
app.add_routes([
    web.get("/", list_all),
    web.post("/user", add_user)
])
register_tortoise(
    app,
    db_url="postgres://artemiev:@/antifragility",
    modules={"models": ["models"]},
    generate_schemas=True
)

if __name__ == "__main__":
    web.run_app(app)
