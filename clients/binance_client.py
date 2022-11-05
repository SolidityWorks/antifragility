from time import time

import aiohttp

from db.models import User

gap = 0.01
HOST = 'https://c2c.binance.com/'
ADS_PTH = 'bapi/c2c/v2/friendly/c2c/adv/search'
AD_PTH = 'bapi/c2c/v2/public/c2c/adv/selected-adv/'
MY_ADS_PTH = 'bapi/c2c/v2/private/c2c/adv/list-by-page'
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
            'cookie': f'p20t=web.{user.id}.{user.auth["cook"]}',
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
    res = await breq(PTS_PTH, user, {})
    return res['data']


async def get_my_ads(user: User):
    res = await breq(MY_ADS_PTH, user, {"inDeal": 1, "rows": 50, "page": 1})
    return res['data']


async def act_orders(user: User):  # payment methods
    res = await breq(ORD_PTH, user, {"page": 1, "rows": 20, "orderStatusList": [0, 1, 2, 3, 5]})
    return res['data'], res['total']


async def get_arch_orders(user: User, part: int = 0, page: int = 1):  # payment methods
    res = await breq(ORD_ARCH_PTH, user, {"page": page or 1, "rows": 50, "startDate": int((time()-m6*(part+1))*1000), "endDate": int((time()-m6*part)*1000)})
    return res['data'], res['total']

m6 = 60*60*24*30*6


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


async def get_ad(aid: str):
    res = await breq(AD_PTH+aid, is_post=False)
    return res.get('data')

