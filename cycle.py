from asyncio import run

from clients.binance_client import get_ads
from db.models import User, ClientStatus, Pair, Fiat
from db.update import ad_proc


async def cycle():
    users = await User\
        .filter(ex_id=1, is_active=True, client__status__gte=ClientStatus.own)\
        .prefetch_related('ex')
    pairs: [Pair] = await users[0].ex.pairs
    while True:
        await tick(pairs)


async def tick(pairs: [Pair]):
    cnt = 0
    suc, err, lp = 0, 0, len(pairs)
    for pair in pairs:
        if (res := await get_ads(pair.coin_id, pair.cur_id, pair.sell, None, 2)).get('data'):  # if isSell else [pt.name for pt in pts])
            pts = [f.pt for f in (await Fiat.all().prefetch_related('pt'))] if pair.sell else await (await pair.cur).pts.filter(rank__gte=0)
            await ad_proc(res, {pt.name for pt in pts})
            suc += 1
            # just process indicate:
            # print(spinner[cnt], end='\r')  # todo: stats prettier
            print('[', end='')
            for x in range(suc+err):
                print(u"\u2588", end='')
            for x in range(lp-suc-err):
                print("_", end='')
            print(']', end='\r')
            cnt = (cnt+1) % 4
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
