from clients.binance_client import get_ads, get_my_pts, balance
from db.models import User, Client, ClientStatus, Ex, Cur, Coin, Pair, Price, Ad, Pt, Fiat, Asset


async def get_bc2c_users():
    return await User.filter(ex_id=1, client__status__gte=ClientStatus.own)


async def upd_fiats():
    for user in await get_bc2c_users():
        my_pts = await get_my_pts(user)
        all_pts = await Pt.all().only('name').values_list('name', flat=True)
        if diffs := set([pt['identifier'] for pt in my_pts]) - set(all_pts):
            await Pt.bulk_create([Pt(name=diff) for diff in diffs])
        for pt in my_pts:
            dtl = pt['fields'][3 if pt['identifier'] == 'Advcash' else 1]['fieldValue']
            await Fiat.update_or_create(id=pt['id'], user=user, pt_id=pt['identifier'], detail=dtl)


async def upd_founds():
    for user in await get_bc2c_users():
        for b in await balance(user):
            d = {"id": f'{b["asset"]}_{user.id}',
                 "coin_id": b["asset"],
                 "user": user,
                 "free": b["free"],
                 "freeze": b["freeze"],
                 "lock": b["locked"]}
            await Asset.update_or_create(**d)


# # # users:
async def user_upd_bc(uid: int, gmail: str, nick: str, cook: str, tok: str) -> {}:  # bc: binance credentials
    client, cr = await Client.get_or_create(gmail=gmail)
    user, cr = await User.get_or_create(uid=uid, client=client, ex=await Ex.get(name="bc2c"))
    # noinspection PyAsyncCall
    user.update_from_dict({'nickName': nick, 'auth': {"cook": cook, "tok": tok}})
    await user.save()
    return user


async def seed_pts(start_page: int = 1, end_page: int = 5):
    i = 0
    for isSell in [0, 1]:
        for cur in await Cur().all():
            for coin in await Coin().all():
                for page in range(start_page, end_page+1):
                    res = await get_ads(coin.id, cur.id, isSell, None, 20, page)  # if isSell else [pt.name for pt in pts])
                    if res.get('data'):
                        for ad in res['data']:
                            pts = [(await Pt.get_or_create(name=a['identifier']))[0] for a in ad['adv']['tradeMethods']]
                            await cur.pts.add(*pts)
                            i += 1
                        if page == 1:
                            await ad_add(res)  # pair upsert
                    else:
                        break
    print('ads processed:', i)


async def ad_add(res):
    adv = res['data'][0]['adv']
    unq = {'coin_id': adv['asset'], 'cur_id': adv['fiatUnit'], 'sell': adv['tradeType'] != 'SELL', 'ex_id': 1}
    add = {'price': float(adv['price']), 'maxFiat': float(adv['dynamicMaxSingleTransAmount']),
           'minFiat': adv['minSingleTransAmount'], 'total': res['total'], 'fee': adv['commissionRate']}
    # ad
    idd = int(adv['advNo']) - 10 ** 19

    if pair := await Pair.get_or_none(**unq).prefetch_related('ad'):
        # todo remove "not pair.ad" cond
        if not pair.ad or pair.ad.id != idd or pair.price != add['price'] or pair.maxFiat != add['maxFiat']:  # todo: separate diffs
            await pair.update_from_dict(add).save()
    else:
        pair = await Pair.create(**unq, **add)

    if not await Ad.exists(id=idd):
        # user for ad
        usr = res['data'][0]['advertiser']
        user, cr = await User.update_or_create(
            uid=usr['userNo'],
            nickName=usr['nickName'],
            ex_id=1
        )
        ad_props = {
            'id': idd,
            'pair': pair,
            'user': user,
        }
        if ad := await Ad.get_or_none(pair=pair):
            await ad.delete()
        await Ad.create(**ad_props)
        # last ad pts
        await pair.pts.clear()
        pts = [await Pt[a['identifier']] for a in adv['tradeMethods']]
        await pair.pts.add(*pts)

    # price upsert  # todo refactor after separate
    p, cr = await Price.get_or_create(price=add['price'], pair=pair)
    if cr:
        pts = locals().get('pts', await pair.pts)
        print(pair, p.price, f"({pair.minFiat}-{pair.maxFiat})", [p.name for p in pts])
