import asyncio
from tortoise import Tortoise

from db.update import upd_fiats, upd_founds, seed_pts, orders_fill
from init import ptg


async def update():
    await Tortoise.generate_schemas()
    # actual
    await upd_fiats()
    await upd_founds()

    # await seed_pts(2, 2)  # lo-o-ong time
    # todo: only first time
    await ptg()
    await orders_fill()


if __name__ == "__main__":
    from loader import cns
    asyncio.run(update())
