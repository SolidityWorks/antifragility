from clients.binance_client import get_pts, get_ads
from db.models import User, Client, ClientStatus, Ex, Found, Cur, Coin, Pair, Price, Ad, Pt


async def upd_found():
    for user in await User.filter(ex_id=1, client__status__gte=ClientStatus.own):
        pts = await get_pts(user)
        for pt in pts:
            dtl = pt['fields'][3 if pt['identifier'] == 'Advcash' else 1]['fieldValue']
            await Found.update_or_create(id=pt['id'], user=user, pt_id=pt['identifier'], detail=dtl)


# # # users:
async def user_upd_bc(uid: int, gmail: str, nick: str, cook: str, tok: str, cur: str = None) -> {}:  # bc: binance credentials
    client, cr = await Client.get_or_create(gmail=gmail)
    user, cr = await User.get_or_create(uid=uid, client=client, ex=await Ex.get(name="bc2c"))
    # noinspection PyAsyncCall
    user.update_from_dict({'nickName': nick, 'auth': {"cook": cook, "tok": tok}})
    await user.save()
    return user


async def seed_pts():
    i = 0
    for isSell in [0, 1]:
        for cur in await Cur().all():
            for coin in await Coin().all():
                for page in range(1, 3):
                    res = await get_ads(coin.id, cur.id, isSell, None, 20, page)  # if isSell else [pt.name for pt in pts])
                    if res.get('data'):
                        if page == 1:
                            # pair upsert
                            await ad_add(res)

                        for ad in res['data']:
                            pts = [(await Pt.get_or_create(name=a['identifier']))[0] for a in ad['adv']['tradeMethods']]
                            await cur.pts.add(*pts)
                            i += 1

                    else:
                        break
    print('ads processed:', i)


async def ad_add(res):
    adv = res['data'][0]['adv']
    unq = {'coin_id': adv['asset'], 'cur_id': adv['fiatUnit'], 'sell': adv['tradeType'] != 'SELL', 'ex_id': 1}
    add = {'fee': adv['commissionRate'], 'last_price': float(adv['price']), 'total': res.get('total')}
    if pair := await Pair.get_or_none(**unq):
        # noinspection PyAsyncCall
        pair.update_from_dict(add)
        await pair.save()
    else:
        pair = await Pair.create(**unq, **add)
    # price upsert
    await Price.get_or_create(price=adv['price'], pair=pair)
    # user for ad
    user, cr = await User.update_or_create(
        uid=res['data'][0]['advertiser']['userNo'],
        nickName=res['data'][0]['advertiser']['nickName'],
        ex_id=1
    )
    # ad
    idd = int(adv['advNo']) - 10 ** 19
    props = {
        'pair': pair,
        'user': user,
        'price': adv['price'],
        'minFiat': float(adv['minSingleTransAmount']),
        'maxFiat': float(adv['dynamicMaxSingleTransAmount']),
    }
    if ad := await Ad.get_or_none(id=idd):
        await ad.update_from_dict(props)
    else:
        ad = await Ad.create(id=idd, **props)
    # ad_pt
    pts = [(await Pt.get_or_create(name=a['identifier']))[0] for a in adv['tradeMethods']]
    await ad.pts.add(*pts)
