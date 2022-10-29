from math import ceil
from time import time

import aiohttp

from db.models import User, Ad, Pair, Pt, Fiat, Order, Client

gap = 0.01
HOST = 'https://c2c.binance.com/'
ADS_PTH = 'bapi/c2c/v2/friendly/c2c/adv/search'
PTS_PTH = 'bapi/c2c/v2/private/c2c/pay-method/user-paymethods'
ORD_PTH = 'bapi/c2c/v2/private/c2c/order-match/order-list'
ORD_ARCH_PTH = 'bapi/c2c/v1/private/c2c/order-match/order-list-archived-involved'
BLNC_URL = 'https://www.binance.com/bapi/asset/v2/private/asset-service/wallet/balance?needBalanceDetail=true'


async def breq(path: str, user: User = None, data=None, is_post=True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
        'Content-Type': 'application/json',
        'clienttype': 'web',
    }
    if user:
        headers.update({
            'csrftoken': user.auth['tok'],
            'cookie': f'p20t=web.{user.uid}.{user.auth["cook"]}',
        })
    async with aiohttp.ClientSession() as session:
        reqf = session.post if is_post else session.get
        # noinspection PyArgumentList
        async with reqf(('' if path.startswith('https://') else HOST) + path, headers=headers, json=data) as response:
            # if response.status == 401:
            #     await hc(user)
            return (await response.json()) or response.status


async def ping(user: User):
    res = await breq('bapi/accounts/v1/public/authcenter/auth', user)
    return res['success']


# async def hc(user: {}):
#     if not await ping(user):
#         msg = 'You need to log in binance.com'
#         await bot.send_message(user['tg_id'], msg)
#         users_db.update({'ran': False}, user['key'])


async def get_my_pts(user: User):  # payment methods
    res = await breq('', user, {})
    return res['data']


async def act_orders(user: User):  # payment methods
    res = await breq(ORD_PTH, user, {"page": 1, "rows": 20, "orderStatusList": [0, 1, 2, 3, 5]})
    return res['data'], res['total']


async def get_arch_orders(user: User, part: int = 0, page: int = 1):  # payment methods
    res = await breq(ORD_ARCH_PTH, user, {"page": page or 1, "rows": 50, "startDate": int((time()-m6*(part+1))*1000), "endDate": int((time()-m6*part)*1000)})
    return res['data'], res['total']


async def arch_orders(user: User, part: int = 0, page: int = 0):  # payment methods
    orders, total = await get_arch_orders(user, part, page)
    if total:
        if page:
            await orders_proc(orders, user)
        else:
            for prev_page in range(ceil(total/50)):
                await arch_orders(user, part, prev_page+1)
            await arch_orders(user, part+1)


m6 = 60*60*24*30*6


async def orders_proc(orders: [{}], user: User):
    for od in orders:
        order = await ordr(od, user)
        if o := await Order.get_or_none(id=order['id']):
            await o.update_from_dict(order).save()
            print('', end=':')
        else:
            await Order.create(**order)
            print('', end='.')


async def ordr(d: {}, user: User):  # class helps to create ad object from input data
    aid: int = int(d['advNo']) - 10 ** 19
    ptsd = {p['id']: p['identifier'] for p in d['payMethods']}
    sell: bool = d['tradeType'] == 'SELL'
    if not (ad := await Ad.get_or_none(id=aid).prefetch_related('pts')):
        pair, = await Pair.get(sell=sell, coin_id=d['asset'], cur_id=d['fiat']),
        ad = await Ad.create(id=aid, price=d['price'], maxFiat=d['totalPrice'], minFiat=d['totalPrice'], pair=pair)
        await ad.pts.add(*[await Pt[pt] for pt in ptsd.values()])

    pt: str = ptsd.get(d['selectedPayId'])

    if sell:  # I receive to this fiat
        fiat: Fiat = await Fiat[d['selectedPayId']] if d['selectedPayId'] else None
    else:  # I pay from this fiat. Search my fiat by pt
        fiats = await Fiat.filter(pt_id=pt, user_id=user.id).prefetch_related('curs')
        fiats = [f for f in fiats if d['fiat'] in [c.id for c in f.curs]]
        if len(fiats) != 1:
            print('WARNING FIATS STRUCTURE:', d['selectedPayId'], pt)
            fiats = [None]
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
        'created_at': int(d['createTime']/1000)
    }


async def balance(user: User, spot0fond1: 0 | 1 = 1):  # payment methods
    res = await breq(
        BLNC_URL,
        user,
        is_post=False
    )
    return res['data'][spot0fond1]['assetBalances'] if res.get('data') else None


async def get_ads(asset: str, cur: str, sell: int = 0, pts: [str] = None, rows: int = 2, page: int = 1):
    payload = {"page": page,
               "rows": rows,
               "payTypes": pts,
               "asset": asset,
               "tradeType": "SELL" if sell else "BUY",
               "fiat": cur,
               # "transAmount": amount
               }
    return await breq(ADS_PTH, None, payload)
