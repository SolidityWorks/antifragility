import asyncio

from tortoise import Tortoise

from db.update import upd_fiats, upd_founds


async def update():
    await Tortoise.generate_schemas()
    # actual
    await upd_fiats()
    await upd_founds()


if __name__ == "__main__":
    from loader import cns
    asyncio.run(update())
