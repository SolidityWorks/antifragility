from asyncio import run
from tortoise import Tortoise

from clients.binance_client import get_ads
from db.update import ad_add
from loader import orm_params
from db.models import User, ClientStatus, Pair


async def cycle():
    await Tortoise.init(**orm_params)
    users = await User\
        .filter(ex_id=1, is_active=True, client__status__gte=ClientStatus.own)\
        .prefetch_related('ex')
    pairs: Pair = await users[0].ex.pairs
    while True:
        await tick(pairs)


async def tick(pairs: [Pair]):
    for pair in pairs:
        if (res := await get_ads(pair.coin_id, pair.cur_id, pair.sell, None, 2)).get('data'):  # if isSell else [pt.name for pt in pts])
            await ad_add(res)
            #     ads[key] = [{"x": time()*1000, "y": ad0['price']}]  # ad0['id'],

    # return ads


if __name__ == "__main__":
    try:
        run(cycle())
    except KeyboardInterrupt:
        print('Stopped.')
