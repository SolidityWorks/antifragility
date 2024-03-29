import asyncio
from math import ceil
from tortoise import Tortoise

from clients.binance_async import spot_prices
from clients.binance_с2с import get_arch_orders
from db.fiat import upd_fiats, upd_founds
from db.models import Client, User, Coin
from db.order import orders_proc


async def update():
    await Tortoise.generate_schemas()
    # actual
    await upd_coin_usdt_rates()
    await upd_fiats()
    await upd_founds()
    await orders_fill()


async def upd_coin_usdt_rates(quote: str = 'RUB'):
    q_coin = await Coin[quote]
    q_coin.rate = 1
    coins = await Coin.filter(id__not=quote).all()
    coin_tickers = (coin.id + quote for coin in coins)
    rates = await spot_prices(*coin_tickers)
    for coin in coins:
        coin.rate = rates.get(coin.id + quote, 1)
    await Coin.bulk_update(coins+[q_coin], ['rate'])


async def orders_fill():
    clients: [Client] = await Client.filter(status__gte=3).prefetch_related('users')
    for client in clients:
        [await arch_orders(user) for user in client.users]  # if not len(await user.orders.limit(1))]  # only for users with no orders


async def arch_orders(user: User, part: int = 0, page: int = 0):  # payment methods
    orders, total = await get_arch_orders(user, part, page)
    if total:
        if page:
            await orders_proc(orders, user)
        else:
            for prev_page in range(ceil(total/50)):
                await arch_orders(user, part, prev_page+1)
            await arch_orders(user, part+1)


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    asyncio.run(update())
