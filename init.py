from asyncio import run
from tortoise import Tortoise

from clients.binance_client import get_ads
from db.ad import ad_proc
from db.models import Cur, Coin, Pt, Ptc, Ex, ExType


async def init():
    await Tortoise.generate_schemas()

    await Coin.bulk_create(Coin(id=c) for c in [
        "USDT",
        "BTC",
        "ETH",
        "BNB",
        "BUSD",
        "RUB",
        "ADA",
        "TRX",
        "SHIB",
        "MATIC",
        "XRP",
        "SOL",
        "WRX",
        "DAI",
        "DOGE",
        "DOT",
        "CAKE",
        "ICP",
    ])
    await Cur.bulk_create(Cur(id=c) for c in [
        "RUB",
        "USD",
        "EUR",
        "TRY",
    ])
    await Ex.create(name="bc2c", type=ExType.p2p)
    # actual payment types seeding
    await seed_pts(1, 2)  # lo-o-ong time
    await pt_ranking()
    await ptg()


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


async def pt_ranking():
    await Pt.filter(name__in=['Payeer']).update(rank=-3)
    await Pt.filter(name__in=['Advcash']).update(rank=-2)
    await Pt.filter(name__in=['RUBfiatbalance']).update(rank=-1)
    await Pt.filter(name__in=['TinkoffNew', 'DenizBank']).update(rank=4)
    await Pt.filter(name__in=['RosBankNew', 'BanktransferTurkey']).update(rank=3)
    await Pt.filter(name__in=['RaiffeisenBank']).update(rank=2)
    await Pt.filter(name__in=['QIWI']).update(rank=5)
    await Pt.filter(name__in=['YandexMoneyNew']).update(rank=6)


async def ptg():
    bc, _ = await Pt.get_or_create(name='BankCards')
    rb, _ = await Pt.get_or_create(name='RussianBanks', parent=bc)
    await (await Pt['RosBankNew']).update_from_dict({'parent': rb}).save()
    await (await Pt['TinkoffNew']).update_from_dict({'parent': rb}).save()
    await (await Pt['RaiffeisenBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['PostBankNew']).update_from_dict({'parent': rb}).save()
    await (await Pt['UralsibBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['HomeCreditBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['MTSBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['AkBarsBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['UniCreditRussia']).update_from_dict({'parent': rb}).save()
    await (await Pt['OTPBankRussia']).update_from_dict({'parent': rb}).save()
    await (await Pt['RussianStandardBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['BCSBank']).update_from_dict({'parent': rb}).save()
    await (await Pt['ABank']).update_from_dict({'parent': rb}).save()
    sbp = await Pt.create(name='SBP', rank=-5, parent=rb)
    await Ptc.create(pt=sbp, blocked=True, cur_id='RUB')
    sbr = await Pt.create(name='Sberbank', rank=-5, parent=rb)
    await Ptc.create(pt=sbr, blocked=True, cur_id='RUB')
    vtb = await Pt.create(name='VTBBank', rank=-5, parent=rb)
    await Ptc.create(pt=vtb, blocked=True, cur_id='RUB')
    otkr = await Pt.create(name='OtkritieBank', rank=-5, parent=rb)
    await Ptc.create(pt=otkr, blocked=True, cur_id='RUB')
    svk = await Pt.create(name='SovkomBank', rank=-5, parent=rb)
    await Ptc.create(pt=svk, blocked=True, cur_id='RUB')
    alf = await Pt.create(name='AlfaBank', rank=-5, parent=rb)
    await Ptc.create(pt=alf, blocked=True, cur_id='RUB')
    await Ptc.create(pt_id='CashDeposit', blocked=True, cur_id='RUB')
    await Ptc.create(pt_id='ABank', cur_id='RUB')
    tb, _ = await Pt.get_or_create(name='TurkBanks', parent=bc)
    await (await Pt['Akbank']).update_from_dict({'parent': tb}).save()
    await (await Pt['alBaraka']).update_from_dict({'parent': tb}).save()
    await (await Pt['SpecificBank']).update_from_dict({'parent': tb}).save()
    await (await Pt['HALKBANK']).update_from_dict({'parent': tb}).save()
    await (await Pt['Fibabanka']).update_from_dict({'parent': tb}).save()
    await (await Pt['BAKAIBANK']).update_from_dict({'parent': tb}).save()
    await (await Pt['KuveytTurk']).update_from_dict({'parent': tb}).save()
    await (await Pt['Ziraat']).update_from_dict({'parent': tb}).save()
    await (await Pt['BanktransferTurkey']).update_from_dict({'parent': tb}).save()
    await (await Pt['BANK']).update_from_dict({'parent': tb}).save()
    await (await Pt['VakifBank']).update_from_dict({'parent': tb}).save()
    await (await Pt['Papara']).update_from_dict({'parent': tb}).save()
    await (await Pt['QNB']).update_from_dict({'parent': tb}).save()
    await (await Pt['ISBANK']).update_from_dict({'parent': tb}).save()
    await (await Pt['Garanti']).update_from_dict({'parent': tb}).save()
    await (await Pt['DenizBank']).update_from_dict({'parent': tb}).save()
    eb, _ = await Pt.get_or_create(name='EuroBanks', parent=bc)
    await (await Pt['SEPA']).update_from_dict({'parent': eb}).save()
    await (await Pt['SEPAinstant']).update_from_dict({'parent': eb}).save()
    await (await Pt['ING']).update_from_dict({'parent': eb}).save()
    await (await Pt['Advcash']).update_from_dict({'parent': eb}).save()
    await (await Pt['CashDeposit']).update_from_dict({'parent': eb}).save()


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    run(init())
