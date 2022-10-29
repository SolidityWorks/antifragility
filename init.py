from asyncio import run
from tortoise import Tortoise

from db.update import seed_pts
from db.models import Cur, Coin, Ex, ExType, Pt, Fcr, Region


async def init():
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
    await seed_pts(1, 2)  # lo-o-ong time
    await pt_ranking()


async def pt_ranking():
    await Pt.filter(name__in=['Payeer']).update(rank=-3)
    await Pt.filter(name__in=['Advcash']).update(rank=-2)
    await Pt.filter(name__in=['RUBfiatbalance']).update(rank=-1)
    await Pt.filter(name__in=['TinkoffNew', 'DenizBank']).update(rank=4)
    await Pt.filter(name__in=['RosBankNew', 'BanktransferTurkey']).update(rank=3)
    await Pt.filter(name__in=['RaiffeisenBank']).update(rank=2)
    await Pt.filter(name__in=['QIWI']).update(rank=5)
    await Pt.filter(name__in=['YandexMoneyNew']).update(rank=6)


async def fiat_cur():
    await Fcr.create(fiat_id=25842082, cur_id='TRY')
    await Fcr.create(fiat_id=25812762, cur_id='USD')
    await Fcr.create(fiat_id=25416699, cur_id='TRY')
    await Fcr.create(fiat_id=25303844, cur_id='USD', region=Region.turkey)
    await Fcr.create(fiat_id=25303844, cur_id='EUR', region=Region.turkey)
    await Fcr.create(fiat_id=25303844, cur_id='TRY', region=Region.turkey)
    await Fcr.create(fiat_id=25303844, cur_id='RUB', region=Region.turkey, blocked=True)
    await Fcr.create(fiat_id=25303608, cur_id='USD', region=Region.turkey)
    await Fcr.create(fiat_id=25303608, cur_id='EUR', region=Region.turkey)
    await Fcr.create(fiat_id=25303608, cur_id='TRY', region=Region.turkey)
    await Fcr.create(fiat_id=25303608, cur_id='RUB', region=Region.turkey, blocked=True)
    await Fcr.create(fiat_id=25236287, cur_id='USD')
    await Fcr.create(fiat_id=25236248, cur_id='TRY')
    await Fcr.create(fiat_id=25236170, cur_id='USD')
    await Fcr.create(fiat_id=25136929, cur_id='TRY')
    await Fcr.create(fiat_id=24956898, cur_id='RUB')
    await Fcr.create(fiat_id=24956617, cur_id='RUB')
    await Fcr.create(fiat_id=24955395, cur_id='TRY')
    await Fcr.create(fiat_id=24951855, cur_id='RUB')
    await Fcr.create(fiat_id=24950350, cur_id='TRY')
    await Fcr.create(fiat_id=20023779, cur_id='RUB')
    await Fcr.create(fiat_id=17750004, cur_id='USD')
    await Fcr.create(fiat_id=17750004, cur_id='EUR')
    await Fcr.create(fiat_id=17750004, cur_id='RUB')
    await Fcr.create(fiat_id=17746529, cur_id='EUR')
    await Fcr.create(fiat_id=17746495, cur_id='USD')
    await Fcr.create(fiat_id=17746422, cur_id='RUB')
    await Fcr.create(fiat_id=16026051, cur_id='RUB')


if __name__ == "__main__":
    from loader import cns
    run(init())
