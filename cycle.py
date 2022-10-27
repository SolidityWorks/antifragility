from asyncio import run

from clients.binance_client import get_ads
from db.update import ad_add
from db.models import User, ClientStatus, Pair


async def cycle():
    users = await User\
        .filter(ex_id=1, is_active=True, client__status__gte=ClientStatus.own)\
        .prefetch_related('ex')
    pairs: Pair = await users[0].ex.pairs
    while True:
        await tick(pairs)


async def tick(pairs: [Pair]):
    global cnt
    for pair in pairs:
        if (res := await get_ads(pair.coin_id, pair.cur_id, pair.sell, None, 2)).get('data'):  # if isSell else [pt.name for pt in pts])
            await ad_add(res)
            # just process indicate:
            print(prgrs[cnt], end='\r')
            cnt = (cnt+1) % 4

cnt = 0
prgrs = ('|', '/', '-', '\\',)


if __name__ == "__main__":
    try:
        from loader import cns
        run(cycle())
    except KeyboardInterrupt:
        print('Stopped.')
