import asyncio

from tortoise import Tortoise

from db.update import upd_fiats, upd_founds, seed_pts
from init import fiat_cur


async def update():
    await Tortoise.generate_schemas()
    # actual
    await upd_fiats()
    await upd_founds()

    await seed_pts(1, 1)  # lo-o-ong time
    # todo: only first time
    await fiat_cur()


if __name__ == "__main__":
    from loader import cns
    asyncio.run(update())
