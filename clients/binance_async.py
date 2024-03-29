import hashlib
import hmac
from asyncio import run
from time import time

from aiohttp import ClientSession

# mixartemev
client = {
    'key': 'p6ZW9WXQkUeHJlyOmZN3n63eX7ReVfVsSdYe4SQxkFNK12PsnHXmLc4538hcuM0G',
    'secret': 'gBbvwj2gcDvLnkbFNnjf8vFEcAvwAY05KeHcu7UFvlVEOyfUgnmfo1kbZtttSXkK'
}
# alena
# client = Spot(key='dtyLk0I4S4zlWMN6sqO1aFtHKfjDcjstTbG2fuSpfZVEvr2NJLnUnSt0UFyCyHGv', secret='EE3tnb8I2IZGYtWUt72wXZ3NrIaKqUkaGFgMoHxRtkTas2y8EuKK0sQg1jcbGwTI')

host = 'https://api.binance.com/'
ws_host = 'wss://stream.binance.com:9443'

c2c_hist = 'sapi/v1/c2c/orderMatch/listUserOrderHistory'
ex_data = 'sapi/v1/convert/exchangeInfo'


async def get_pub(path: str, params: {} = None):
    async with ClientSession() as session:
        resp = await session.get(host + path, params=params)
        return await resp.json()


async def get_prv(path: str, cln: {}, params: {} = None):
    def sign(prms: {}) -> {}:
        """Makes a signature and adds it to the params dictionary."""
        data = list(prms.items())
        query: str = '&'.join(["{}={}".format(d[0], d[1]) for d in data])
        m = hmac.new(cln['secret'].encode(), query.encode(), hashlib.sha256)
        prms.update({'signature': m.hexdigest()})
        return prms

    headers = {'X-MBX-APIKEY': cln['key']}
    params.update({'timestamp': f'{round(time() * 1000)}'})
    params = sign(params)

    async with ClientSession() as session:
        resp = await session.get(host + path, headers=headers, params=params)
        return await resp.json()


async def spot_prices(*tickers: str):
    symbols = '["' + '","'.join(tickers) + '"]'
    resp = await get_pub('api/v3/ticker/price', {'symbols': symbols} if tickers else None)
    return {r['symbol']: float(r['price']) for r in resp} if type(resp) is list else {}


async def c2c_hst(user: {}, tt: str):
    resp = await get_prv(c2c_hist, user, {'tradeType': tt})
    return resp['data'], resp['total']


# # spot assets
# a = client.user_asset()
# print(a)
#
# # funding assets
# f = client.funding_wallet()
# print(f)
#
# # transfer
# # t = client.user_universal_transfer(type='FUNDING_MAIN', asset='BUSD', amount=11)
# # print(t)
#
# n = client.ticker_price('USDTRUB')
#
# r = client.enable_fast_withdraw()
# r = client.withdraw(coin='SHIB', amount=100000, walletType=1, address='0x2469f1a2aa61dba2107d9905d94f1efa9f60eadc', network='BSC', withdrawOrderId=357058112)
# print(r)


if __name__ == "__main__":
    res = run(spot_prices())
    # res = run(c2c_hst(client, 'BUY'))
    print(res)
