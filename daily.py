from tortoise import run_async, Tortoise

from loader import orm_params
from db.update import upd_fiats


async def update():
    await Tortoise.init(**orm_params)
    await Tortoise.generate_schemas()
    # actual
    await upd_fiats()
    # todo: Founds upsert..


if __name__ == "__main__":
    run_async(update())
