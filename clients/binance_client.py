import aiohttp

from db.models import User

gap = 0.01
URL_SRC = 'https://c2c.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
prgrs = '/', '-', '\\', '|'

bnks = 'banks', 'ym', 'qiwi'


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
        async with reqf(('' if path.startswith('https://') else 'https://c2c.binance.com/') + path, headers=headers, json=data) as response:
            # if response.status == 401:
            #     await hc(user)
            return (await response.json()) or response.status


async def ping(user: dict):
    res = await breq('bapi/accounts/v1/public/authcenter/auth', user)
    return res['success']


# async def hc(user: {}):
#     if not await ping(user):
#         msg = 'You need to log in binance.com'
#         await bot.send_message(user['tg_id'], msg)
#         users_db.update({'ran': False}, user['key'])


async def get_pts(user: User):  # payment methods
    res = await breq('bapi/c2c/v2/private/c2c/pay-method/user-paymethods', user, {})
    return res['data']


async def act_orders(user: dict):  # payment methods
    res = await breq('bapi/c2c/v2/private/c2c/order-match/order-list', user,
                     {"page": 1, "rows": 10, "orderStatusList": [0, 1, 2, 3, 5]})
    return res['data']


async def balance(user: dict, spot0fond1: 0 | 1 = 1):  # payment methods
    res = await breq(
        'https://www.binance.com/bapi/asset/v2/private/asset-service/wallet/balance?needBalanceDetail=true', user,
        is_post=False)
    return res['data'][spot0fond1]['assetBalances'] if res.get('data') else None


async def get_ads(asset: str, cur: str, sell: int = 0, pts: [str] = None, rows: int = 2, page: int = 1):
    payload = {"page": 1,
               "rows": rows,
               "payTypes": pts,
               "asset": asset,
               "tradeType": "SELL" if sell else "BUY",
               "fiat": cur,
               # "transAmount": amount
               }
    return await breq(URL_SRC, None, payload)
