from asyncio import run
from enum import Enum, IntEnum
from aiohttp import ClientSession


class Country(Enum):
    RUS = 'RUS'
    TUR = 'TUR'
    GEO = 'GEO'
    VNM = 'VNM'
    KAZ = 'KAZ'
    KOR = 'KOR'
    UZB = 'UZB'


class Cur(IntEnum):
    RUB = 810
    USD = 840
    EUR = 978
    GEL = 981
    TL = 949


async def korona_rate(to: Country, rcv_amount: int, cur: Cur = Cur.USD) -> float:
    params = {
        'sendingCountryId': Country.RUS.value,
        'sendingCurrencyId': int(Cur.RUB),
        'receivingCountryId': to.value,
        'receivingCurrencyId': int(cur),
        'paymentMethod': 'debitCard',
        'receivingAmount': rcv_amount,
        'receivingMethod': 'cash',
        'paidNotificationEnabled': 'false',
    }
    async with ClientSession() as session:
        resp = await session.get('https://koronapay.com/transfers/online/api/transfers/tariffs', params=params)
        if res := await resp.json():
            return res[0]['exchangeRate']


if __name__ == "__main__":
    res = run(korona_rate(Country.GEO, 1000, Cur.USD))
    print(res)
