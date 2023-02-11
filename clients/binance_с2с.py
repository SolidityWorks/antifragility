from asyncio import run
from time import time

import aiohttp

from db.models import User

gap = 0.01
HOST = 'https://c2c.binance.com/'
ADS = 'bapi/c2c/v2/friendly/c2c/adv/search'
AD = 'bapi/c2c/v2/public/c2c/adv/selected-adv/'
AD_UPD = 'bapi/c2c/v3/private/c2c/adv/update'
AD_UPD_ST = 'bapi/c2c/v2/private/c2c/adv/update-status'
MY_ADS = 'bapi/c2c/v2/private/c2c/adv/list-by-page'
PTS = 'bapi/c2c/v2/private/c2c/pay-method/user-paymethods'
ORD = 'bapi/c2c/v2/private/c2c/order-match/order-list'
ORD_ARCH = 'bapi/c2c/v1/private/c2c/order-match/order-list-archived-involved'
CUR_MIN_AMT = 'bapi/c2c/v1/private/c2c/sys-config/adv-trans-amount-limit'
RATES = 'bapi/c2c/v1/private/c2c/merchant/get-exchange-rate-list'
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
    res = await breq(PTS, user, {})
    return res['data']


async def get_my_ads(user: User):
    res = await breq(MY_ADS, user, {"inDeal": 1, "rows": 50, "page": 1})
    return res['data']


async def act_orders(user: User):  # payment methods
    res = await breq(ORD, user, {"page": 1, "rows": 20, "orderStatusList": [0, 1, 2, 3, 5]})
    return res['data'], res['total']


async def get_arch_orders(user: User, part: int = 0, page: int = 1):  # payment methods
    res = await breq(ORD_ARCH, user,
                     {"page": page or 1, "rows": 50, "startDate": int((time() - m6 * (part + 1)) * 1000),
                      "endDate": int((time() - m6 * part) * 1000)})
    return res['data'], res['total']


m6 = 60 * 60 * 24 * 30 * 6


async def balance(user: User, spot0fond1: 0 | 1 = 1):  # payment methods
    res = await breq(
        BLNC_URL,
        user,
        is_post=False
    )
    return res['data'][spot0fond1]['assetBalances'] if res.get('data') else None


async def get_ads(asset: str, cur: str, sell: int = 0, pts: [str] = None, rows: int = 20, page: int = 1):
    payload = {"page": page,
               "rows": rows,
               "payTypes": pts,
               "asset": asset,
               "tradeType": "SELL" if sell else "BUY",
               "fiat": cur,
               # "transAmount": amount
               }
    return await breq(ADS, None, payload)


async def get_ad(aid: str):
    res = await breq(AD + aid, is_post=False)
    return res.get('data')


async def upd_ad():  # user, data: {}
    user = await User.get(nickName='Deals')
    data = {"asset": "RUB",
            "fiatUnit": "RUB",
            "priceType": 1,
            # "priceScale": 2,
            "advNo": 11419177391185489920,
            "autoReplyMsg": "Взаимный лайк приветствуется:)\nЕсли усну, напишите сюда плиз или в tg: @ex212",
            "initAmount": 50000,
            "payTimeLimit": 30,
            "price": 1.00,
            "priceFloatingRatio": 100.12,
            "minSingleTransAmount": 500,
            "maxSingleTransAmount": 870000,
            "remarks": "Оплачиваю быстро.\n",
            "tradeMethods": [
                {"identifier": "RaiffeisenBank"},
                {"identifier": "RosBankNew"},
                {"identifier": "TinkoffNew"},
                {"identifier": "QIWI"},
                {"identifier": "YandexMoneyNew"}],
            "tradeType": "BUY",
            "launchCountry": []  # "AE", "TR"
            }
    res = await breq(AD_UPD, user, data)
    return res.get('data')


async def upd_ad_status(aid: int, pub: bool = True):  # user, data: {}
    user = await User.get(nickName='Deals')
    data = {"advNos": [f"1{aid}"], "advStatus": int(pub)}
    res = await breq(AD_UPD_ST, user, data)
    return res.get('data')


async def cur_min_amount(cur: str = 'RUB', coin: str = 'USDT'):  # user, data: {}
    user = await User.get(nickName='Deals')
    data = {"asset": coin, "fiatCurrency": cur, "tradeType": "BUY", "limitScene": "mass"}
    res = await breq(CUR_MIN_AMT, user, data)
    return res.get('data')


async def get_rates():  # user, data: {}
    user = await User.get(nickName='Deals')
    res = await breq(RATES, user, is_post=False)
    return {rate['fiatCurrency']: float(rate['exchangeRate']) for rate in res.get('data')}


if __name__ == "__main__":
    try:
        from loader import cns

        # run(upd_ad())
        run(get_rates())
    except KeyboardInterrupt:
        print('Stopped.')
