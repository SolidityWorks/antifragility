from tortoise import run_async, Tortoise

from clients.binance_client import get_ads
from db.update import upd_fiats
from loader import orm_params
from db.models import Pt, Cur, Coin, Ex, ExType


async def seed_pts():
    i = 0
    for isSell in [0, 1]:
        for cur in await Cur().all():
            for coin in await Coin().all():
                for page in range(5, 15):
                    res = await get_ads(coin.id, cur.id, isSell, None, 20, page)  # if isSell else [pt.name for pt in pts])
                    for ad in res:
                        for pt in ad['adv']['tradeMethods']:
                            pto, cr = await Pt.update_or_create(name=pt['identifier'])
                            await pto.curs.add(cur)
                        i += 1
    print('ads processed:', i)


async def seed():
    await Tortoise.init(**orm_params)
    await Tortoise.generate_schemas()

    #
    await Coin.create(id="USDT")
    await Coin.create(id="BTC")
    await Coin.create(id="ETH")
    await Coin.create(id="BNB")
    await Coin.create(id="BUSD")
    # await Coin.create(id="RUB")

    #
    await Ex.create(name="bc2c", type=ExType.p2p)

    ##########

    r = await Cur.create(id="RUB")
    u = await Cur.create(id="USD")
    e = await Cur.create(id="EUR")
    t = await Cur.create(id="TRY")

    await seed_pts()  # lo-o-ong time

    await upd_fiats()
    # await Pt.create(name="CashInPerson", rank=0)  # blocked in Russia
    # await Pt.create(name="BANK", rank=1)  # blocked in Russia
    # #
    # await Pt.create(name="Advcash", rank=-2)
    # await Pt.create(name="Payeer", rank=-3)
    # #
    # # # # Russia
    # await Pt.create(name="TinkoffNew", rank=4)
    # await Pt.create(name="RosBankNew", rank=3)
    # await Pt.create(name="PostBankRussia", rank=2)
    # await Pt.create(name="UralsibBank", rank=2)
    # await Pt.create(name="RaiffeisenBankRussia", rank=2)
    # await Pt.create(name="BCSBank", rank=2)
    # await Pt.create(name="HomeCreditBank", rank=2)
    # await Pt.create(name="VostochnyBank", rank=2)
    # await Pt.create(name="RussianStandardBank", rank=2)
    # await Pt.create(name="ABank", rank=2)  # blocked in Russia
    # await Pt.create(name="MTSBank", rank=2)
    # await Pt.create(name="SpecificBank", rank=2)
    # #
    # await Pt.create(name="YandexMoneyNew", rank=5)
    # await Pt.create(name="QIWI", rank=6)
    # #
    # await Pt.create(name="RUBfiatbalance", rank=-1)
    # #
    # await Pt.create(name="BanktransferTurkey", rank=3)
    # await Pt.create(name="alBaraka", rank=3)
    # await Pt.create(name="Akbank", rank=3)
    # await Pt.create(name="DenizBank", rank=4)
    # await Pt.create(name="Garanti", rank=3)
    # await Pt.create(name="HALKBANK", rank=3)
    # await Pt.create(name="KuveytTurk", rank=3)
    # await Pt.create(name="VakifBank", rank=3)
    # await Pt.create(name="Ziraat", rank=3)
    # #
    # await Pt.create(name="KoronaPay", rank=2)  # blocked in Russia

    # todo: Fiats upsert..
    # # And then Limits seed
    # rus_banks = await PtGroup(name="rus banks", cur=r)
    # ym = await PtGroup(name="ym", cur=r)
    # qiwi = await PtGroup(name="qiwi", cur=r)
    # b_fiat_rub = await PtGroup(name="b_fiat_rub", cur=r)
    # adv_rub = await PtGroup(name="adv_rub", cur=r)
    # adv_usd = await PtGroup(name="adv_usd", cur=u)
    # adv_eur = await PtGroup(name="adv_eur", cur=e)
    # payer_rub = await PtGroup(name="payer_rub", cur=r)
    # payer_usd = await PtGroup(name="payer_usd", cur=u)
    # payer_eur = await PtGroup(name="payer_eur", cur=e)
    # korona_rub = await PtGroup(name="korona_rub", cur=r)
    # korona_usd = await PtGroup(name="korona_usd", cur=u)
    # korona_eur = await PtGroup(name="korona_eur", cur=e)
    # korona_try = await PtGroup(name="korona_try", cur=t)
    # cash_bank = await PtGroup(name="cash_bank", cur=t)

if __name__ == "__main__":
    run_async(seed())
