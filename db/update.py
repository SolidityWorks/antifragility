from clients.binance_client import get_ads, get_my_pts, balance
from db.models import User, Client, ClientStatus, Ex, Cur, Coin, Pair, Ad, Pt, Fiat, Asset


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
                            await ad_proc(res)  # pair upsert
                    else:
                        break
    print('ads processed:', i)


async def ad_proc(res):
    adv = res['data'][0]['adv']
    pair_unq = {'coin_id': adv['asset'], 'cur_id': adv['fiatUnit'], 'sell': adv['tradeType'] != 'SELL', 'ex_id': 1}
    pair_upd = {'total': int(res['total']), 'fee': float(adv['commissionRate'])}

    # Pair
    if pair := await Pair.get_or_none(**pair_unq):
        if pair.total != pair_upd['total']:  # or pair.fee != pair_upd['maxFiat']:
            await pair.update_from_dict(pair_upd).save()
    else:
        pair: Pair = await Pair.create(**pair_unq, **pair_upd)

    # Pt
    pts_new: {str} = set(pt['identifier'] for pt in adv['tradeMethods'])
    pts: [Pt] = []

    # Ad
    idd = int(adv['advNo']) - 10 ** 19
    ad_upd = {'price': float(adv['price']), 'maxFiat': float(adv['dynamicMaxSingleTransAmount']), 'minFiat': adv['minSingleTransAmount']}
    if ad := await Ad.get_or_none(id=idd).prefetch_related('pts'):
        pts_old: {str} = set(pt.name for pt in ad.pts)
        if ad.price != ad_upd['price'] or ad.maxFiat != ad_upd['maxFiat']:  # or ad.minFiat != ad_upd['minFiat']  # todo: separate diffs
            await ad.update_from_dict(ad_upd).save()
        if pts_old != pts_new:
            await ad.pts.clear()
            pts: [Pt] = [await Pt[pt['identifier']] for pt in adv['tradeMethods']]
            await ad.pts.add(*pts)

    else:
        # user for ad
        usr = res['data'][0]['advertiser']
        usr_add = {'nickName': usr['nickName'], 'ex_id': 1}
        if not (user := await User.get_or_none(uid=usr['userNo'])):
            user: User = await User.create(uid=usr['userNo'], nickName=usr['nickName'], ex_id=1)
        ad: Ad = await Ad.create(id=idd, pair=pair, user=user, **ad_upd)

        # pts
        pts: [Pt] = pts or [await Pt[pt['identifier']] for pt in adv['tradeMethods']]
        await ad.pts.add(*pts)

    if pts:
        print(pair, ad.price, f"({ad.minFiat}-{ad.maxFiat})", list(pts_new))
