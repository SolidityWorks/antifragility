from tortoise import run_async, Tortoise

from db.update import upd_found, seed_pts
from loader import orm_params
from db.models import Cur, Coin, Ex, ExType


async def init():
    await Coin.bulk_create(Coin(id=c) for c in [
        "USDT",
        "BTC",
        "ETH",
        "BNB",
        "BUSD",
        "RUB",
        "ADA",
        "TRX",
        "SHIB",
        "MATIC",
        "XRP",
        "SOL",
        "WRX",
        "DAI",
        "DOGE",
        "DOT",
    ])
    await Cur.bulk_create(Cur(id=c) for c in [
        "RUB",
        "USD",
        "EUR",
        "TRY",
    ])
    await Ex.create(name="bc2c", type=ExType.p2p)


async def seed():
    await Tortoise.init(**orm_params)
    await Tortoise.generate_schemas()

    # await init()

    await seed_pts()  # lo-o-ong time
    await upd_found()
    # todo: Fiats upsert..


if __name__ == "__main__":
    run_async(seed())
