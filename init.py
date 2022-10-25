from tortoise import run_async, Tortoise

from db.update import seed_pts
from loader import orm_params
from db.models import Cur, Coin, Ex, ExType, Pt


async def pt_ranking():
    await Pt.filter(name__in=['Payeer']).update(rank=-3)
    await Pt.filter(name__in=['Advcash']).update(rank=-2)
    await Pt.filter(name__in=['RUBfiatbalance']).update(rank=-1)
    await Pt.filter(name__in=['TinkoffNew', 'DenizBank']).update(rank=4)
    await Pt.filter(name__in=['RosBankNew', 'BanktransferTurkey']).update(rank=3)
    await Pt.filter(name__in=['RaiffeisenBank']).update(rank=2)
    await Pt.filter(name__in=['QIWI']).update(rank=5)
    await Pt.filter(name__in=['YandexMoneyNew']).update(rank=6)


async def init():
    await Tortoise.init(**orm_params)
    await Tortoise.generate_schemas()

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
    # actual payment types seeding
    await seed_pts()  # lo-o-ong time
    await pt_ranking()


if __name__ == "__main__":
    run_async(init())
