from asyncio import run

from clients.binance_client import get_ads, get_my_ads
from db.models import Pair, Fiat, Ad, Pt
from db.update import ad_proc, get_bc2c_users


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
            pts = [f.pt for f in (await Fiat.all().prefetch_related('pt'))] if pair.sell else await (await pair.cur).pts.filter(rank__gte=0)
            await ad_proc(res, {pt.name for pt in pts})
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


async def my_ads_actualize():
    for user in await get_bc2c_users():
        res = await get_my_ads(user)
        for ad in res:
            pair = await Pair.get(coin=ad['asset'], cur=ad['fiatUnit'], sell=ad['tradeType'] == 'SELL')
            ap = {
                'pair': pair,
                'price': ad['price'],
                'minFiat': ad['minSingleTransAmount'],
                'maxFiat': ad['surplusAmount'],
                'user_id': user.id,
                'detail': ad['remarks'],
                'autoMsg': ad['autoReplyMsg'],
            }
            adv, cr = await Ad.update_or_create(ap, id=int(ad['advNo']) - 10 ** 19)
            await adv.pts.add(*[await Pt[a['identifier']] for a in ad['tradeMethods']])


if __name__ == "__main__":
    try:
        from loader import cns
        run(cycle())
        run(my_ads_actualize())
    except KeyboardInterrupt:
        print('Stopped.')
