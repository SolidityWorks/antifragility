from asyncio import run

from clients.binance_client import get_ads
from db.models import User, ClientStatus, Pair, Fiat
from db.update import ad_proc


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
            pts = [f.pt for f in (await Fiat.all().prefetch_related('pt'))] if pair.sell else await (await pair.cur).pts.filter(rank__gte=0)
            await ad_proc(res, {pt.name for pt in pts})
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
