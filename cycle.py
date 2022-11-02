from asyncio import run

from clients.binance_client import get_ads, get_my_ads
from db.models import Pair, Fiat, Ad, Pt
from db.ad import ad_proc
from db.user import get_bc2c_users


async def cycle():
    if users := await get_bc2c_users(['ex']):
        pairs: [Pair] = await users[0].ex.pairs
        while True:
            await tick(pairs)


async def tick(pairs: [Pair]):
    cnt = 0
    suc, err, lp = 0, 0, len(pairs)
    for pair in pairs:
        if (res := await get_ads(pair.coin_id, pair.cur_id, pair.sell, None, 2)).get('data'):  # if isSell else [pt.name for pt in pts])
            if pair.sell:
                ptcs = [f.ptc for f in (await Fiat.all().prefetch_related('ptc'))]
                pts = {ptc.pt_id for ptc in ptcs}
            else:
                pts = await (await pair.cur).pts.filter(rank__gte=0)
                pts = {pt.name for pt in pts}
            await ad_proc(res, pts)
            suc += 1
            # just process indicate:
            # print(spinner[cnt], end='\r')  # todo: stats prettier
            print('[', end='')
            for x in range(suc + err):
                print(u"\u2588", end='')
            for x in range(lp - suc - err):
                print("_", end='')
            print(']', end='\r')
            cnt = (cnt + 1) % 4
        else:
            pair.total = 0
            await pair.save()
            err += 1
            print(f'NO Ads for pair {pair.id}: {pair}')
    print(f'\nSuccess: {suc}, Error: {err}, All: {lp}\n')


spinner = ('|', '/', '-', '\\',)


if __name__ == "__main__":
    try:
        from loader import cns
        run(cycle())
    except KeyboardInterrupt:
        print('Stopped.')
