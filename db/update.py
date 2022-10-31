from clients.binance_client import get_ads, get_my_pts, balance, arch_orders
from db.models import User, Client, ClientStatus, Ex, Cur, Coin, Pair, Ad, Pt, Fiat, Asset, Order, OrderStatus, Ptc


async def get_bc2c_users() -> [User]:
    return await User.filter(ex_id=1, client__status__gte=ClientStatus.own)  # .all()  # the same result


async def upd_fiats():
    for user in await get_bc2c_users():
        my_pts = await get_my_pts(user)
        all_pts = await Pt.all().only('name').values_list('name', flat=True)
        if diffs := set([pt['identifier'] for pt in my_pts]) - set(all_pts):
            await Pt.bulk_create([Pt(name=diff) for diff in diffs])
        for pt in my_pts:
            dtl = pt['fields'][3 if pt['identifier'] == 'Advcash' else 1]['fieldValue']
            ptc, _ = await Ptc.get_or_create(cur_id=fiat_cur_map[pt['id']], pt_id=pt['identifier'])
            await Fiat.update_or_create(id=pt['id'], user=user, ptc=ptc, detail=dtl)


fiat_cur_map: {} = {
    25842082: 'EUR',
    25812762: 'EUR',
    25416699: 'TRY',
    25303844: 'TRY',
    25303608: 'TRY',
    25236287: 'USD',
    25236248: 'USD',
    25236170: 'USD',
    25136929: 'TRY',
    24956898: 'RUB',
    24956617: 'RUB',
    24955395: 'TRY',
    24951855: 'RUB',
    24950350: 'TRY',
    20023779: 'RUB',
    17750004: 'RUB',
    17746529: 'EUR',
    17746495: 'USD',
    17746422: 'RUB',
    16026051: 'RUB',
}


async def upd_founds():
    for user in await get_bc2c_users():
        for b in await balance(user):
            key = f'{b["asset"]}_{user.id}'
            d = {"coin_id": b["asset"],
                 "user": user,
                 "free": b["free"],
                 "freeze": b["freeze"],
                 "lock": b["locked"]}
            if a := await Asset.get_or_none(id=key):
                await a.update_from_dict(d).save()
            else:
                await Asset.create(id=key, **d)


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
        for cur in await Cur().all().prefetch_related('pts'):
            for coin in await Coin().all():
                for page in range(start_page, end_page+1):
                    res = await get_ads(coin.id, cur.id, isSell, None, 20, page)  # if isSell else [pt.name for pt in pts])
                    if res.get('data'):
                        pts = set()
                        for ad in res['data']:
                            [pts.add(a['identifier']) for a in ad['adv']['tradeMethods']]
                            i += 1
                        pts = [(await Pt.update_or_create(name=pt))[0] for pt in pts]
                        await cur.pts.add(*pts)
                        if page == 1:
                            await ad_proc(res)  # pair upsert
                    else:
                        break
    print('ads processed:', i)


async def ad_proc(res: {}, pts_cur: {str} = None):
    adv = res['data'][0]['adv']
    pair_unq = {'coin_id': adv['asset'], 'cur_id': adv['fiatUnit'], 'sell': adv['tradeType'] != 'SELL', 'ex_id': 1}
    pair_upd = {'total': int(res['total']), 'fee': float(adv['commissionRate'])}

    # Pair
    if pair := await Pair.get_or_none(**pair_unq):
        if pair.total != pair_upd['total'] or pair.fee != pair_upd['fee']:
            await pair.update_from_dict(pair_upd).save()
    else:
        pair: Pair = await Pair.create(**pair_unq, **pair_upd)

    # Pt
    pts_new: {str} = set(pt['identifier'] for pt in adv['tradeMethods'])
    if pts_cur:  # pts filter for cycle update
        pts_new = pts_new  # & pts_cur  # todo: temporary disable pts filtering
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
            pts: [Pt] = [await Pt[pt] for pt in pts_new]
            await ad.pts.add(*pts)

    else:
        # user for ad
        usr = res['data'][0]['advertiser']
        if not (user := await User.get_or_none(uid=usr['userNo'])):
            user: User = await User.create(uid=usr['userNo'], nickName=usr['nickName'], ex_id=1)
        ad: Ad = await Ad.create(id=idd, pair=pair, user=user, **ad_upd)

        # pts
        pts: [Pt] = pts or [await Pt[pt] for pt in pts_new]
        await ad.pts.add(*pts)

    # if pts:
    print(f"{pair.id}: {pair} [{pair.total}] {ad.price} * ({ad.minFiat}-{ad.maxFiat}) :", *pts_new)


async def orders_fill():
    clients: [Client] = await Client.filter(status__gte=3).prefetch_related('users')
    for client in clients:
        [await arch_orders(user) for user in client.users]


async def ordr(d: {}, user: User):  # class helps to create ad object from input data
    aid: int = int(d['advNo']) - 10 ** 19
    ptsd = {p['id']: p['identifier'] for p in d['payMethods']}
    sell: bool = d['tradeType'] == 'SELL'
    if not (ad := await Ad.get_or_none(id=aid).prefetch_related('pts')):
        pair = await Pair.get(sell=sell, coin_id=d['asset'], cur_id=d['fiat'])
        ad = await Ad.create(id=aid, price=d['price'], maxFiat=d['totalPrice'], minFiat=d['totalPrice'], pair=pair)
        await ad.pts.add(*[await Pt[pt] for pt in ptsd.values()])

    pt: str = ptsd.get(d['selectedPayId'])

    if sell:  # I receive to this fiat
        fiat: Fiat = await Fiat[d['selectedPayId']] if d['selectedPayId'] else None
    else:  # I pay from this fiat. Search my fiat by pt
        fiats = await Fiat.filter(pt_id=pt, user_id=user.id).prefetch_related('curs')
        fiats = [f for f in fiats if d['fiat'] in [c.id for c in f.curs]]
        if len(fiats) != 1:
            print('WARNING FIATS STRUCTURE:', fiats)
        fiat = fiats[0]

    return {
        'id': int(d['orderNumber']) - 2*10**19,
        'ad_id': aid,
        'amount': float(d['amount']),
        'pt_id': pt,
        'fiat': fiat,
        'user': user,
        # 'arch': d['archived'],
        'status': d['orderStatus'],
    }
