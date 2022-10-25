from asyncio import run

from tortoise import Tortoise, ModelMeta
from tortoise.backends.asyncpg.client import TransactionWrapper
from tortoise.signals import Signals

from clients.binance_client import get_ads
from db.update import ad_add
from loader import orm_params
from db.models import User, ClientStatus, Pair, Price


async def watchdog(meta: ModelMeta, price: Price, cr: bool, tw: TransactionWrapper, e):
    print(price.pair, price.price)


async def cycle():
    await Tortoise.init(**orm_params)

    Price.register_listener(Signals.post_save, watchdog)

    users = await User\
        .filter(ex_id=1, is_active=True, client__status__gte=ClientStatus.own)\
        .prefetch_related('ex')
    pairs: Pair = await users[0].ex.pairs
    while True:
        await tick(pairs)


cnt = 0
prgrs = ('|', '/', '-', '\\',)


async def tick(pairs: [Pair]):
    global cnt
    for pair in pairs:
        if (res := await get_ads(pair.coin_id, pair.cur_id, pair.sell, None, 2)).get('data'):  # if isSell else [pt.name for pt in pts])
            await ad_add(res)
            # just process indicate:
            print(prgrs[cnt], end='\r')
            cnt = (cnt+1) % 4


if __name__ == "__main__":
    try:
        run(cycle())
    except KeyboardInterrupt:
        print('Stopped.')
