from asyncio import run
from tortoise import Tortoise

from clients.binance_client import get_ads
from loader import orm_params
from db.models import Cur, Coin, Pt, Client, User, ClientStatus, Pair, Ex, Ad


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
        if res := (await get_ads(pair.coin_id, pair.cur_id, pair.sell, None, 2)).get('data'):  # if isSell else [pt.name for pt in pts])
            ad0 = res[0]['adv']
            u, cr = await User.update_or_create(
                uid=res[0]['advertiser']['userNo'],
                nickName=res[0]['advertiser']['nickName'],
                ex_id=1
            )
            await Ad.update_or_create(
                id=int(ad0['advNo']) - 10 ** 19,
                pair=pair,
                user=u,
                minFiat=float(ad0['minSingleTransAmount']),
                maxFiat=float(ad0['dynamicMaxSingleTransAmount'])
            )
            if pair.price != (price := float(ad0['price'])):
                pair.price = price
                await pair.save()
            #     unq = {k: v for k, v in ad0.items() if k in ['coin', 'cur', 'is_sell', 'ex']}
            #
            #     if ad0['id'] in ids:
            #         ad0['updated_at'] = datetime.now()
            #         Ad.get(**unq).set(**ad0)
            #     else:
            #         if ba := Ad.get(**unq):
            #             ba.delete()
            #         Ad(**ad0)
            #
            #     key = f"{coin}{cur.name}{('f', 't')[isSell]}"
            #     if last_price.get(key) != ad0['price']:
            #         p = Prices(res[0]['adv'], ad0['pts'], 'bc2c')
            #         Price(**p.__dict__)
            #
            #     ads[key] = [{"x": time()*1000, "y": ad0['price']}]  # ad0['id'],

    # return ads


if __name__ == "__main__":
    try:
        run(cycle())
    except KeyboardInterrupt:
        print('Stopped.')
