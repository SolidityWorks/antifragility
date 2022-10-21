from asyncio import run
from tortoise import Tortoise

from clients.binance_client import get_ads
from loader import orm_params
from db.models import Cur, Coin, Pt


async def tick():
    i = 0
    for isSell in [0, 1]:
        for cur in await Cur().all():
            # pts = await Pt.filter(rank__gt=2)  # no pt filter for sales
            for coin in await Coin().all():
                for page in range(10, 15):
                    res = await get_ads(coin.id, cur.id, isSell, None, page)  # if isSell else [pt.name for pt in pts])
                    for ad in res:
                        for pt in ad['adv']['tradeMethods']:
                            pto, cr = await Pt.update_or_create(name=pt['identifier'])
                            await pto.curs.add(cur)
                        i += 1
    print('ads processed:', i)
    pass
                #ad0 = Ads(res[0]['adv'], pts, 'bc2c').__dict__
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
        run(Tortoise.init(**orm_params))
        run(tick())
    except KeyboardInterrupt:
        print('Stopped.')
