from asyncio import run


async def tick():
    for cur in select(c for c in Cur if c.name == 'RUB')[:].to_list():
        for isSell in (0, 1):
            pts = cur.pts.select(lambda pt: pt.rank > 0)[:]  # no pt filter for sales
            for coin in cur.coins.name:
                res = await get_ads(coin, cur.name, isSell, None if isSell else [pt.name for pt in pts])
                ad0 = Ads(res[0]['adv'], pts, 'bc2c').__dict__
                unq = {k: v for k, v in ad0.items() if k in ['coin', 'cur', 'is_sell', 'ex']}

                if ad0['id'] in ids:
                    ad0['updated_at'] = datetime.now()
                    Ad.get(**unq).set(**ad0)
                else:
                    if ba := Ad.get(**unq):
                        ba.delete()
                    Ad(**ad0)

                key = f"{coin}{cur.name}{('f', 't')[isSell]}"
                if last_price.get(key) != ad0['price']:
                    p = Prices(res[0]['adv'], ad0['pts'], 'bc2c')
                    Price(**p.__dict__)

                ads[key] = [{"x": time()*1000, "y": ad0['price']}]  # ad0['id'],



    return ads


if __name__ == "__main__":
    try:
        run(tick())
    except KeyboardInterrupt:
        print('Stopped.')
