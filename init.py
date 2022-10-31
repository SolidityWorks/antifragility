from asyncio import run
from tortoise import Tortoise

from db.update import seed_pts
from db.models import Cur, Coin, Ex, ExType, Pt, Ptc


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
    ])
    await Cur.bulk_create(Cur(id=c) for c in [
        "RUB",
        "USD",
        "EUR",
        "TRY",
    ])
    await Ex.create(name="bc2c", type=ExType.p2p)
    # actual payment types seeding
    await seed_pts(1, 1)  # lo-o-ong time
    sbp = await Pt.create(name='SBP', rank=-1)
    await Ptc.create(pt=sbp, blocked=True, cur_id='RUB')
    await Ptc.create(pt_id='CashDeposit', blocked=True, cur_id='RUB')
    await pt_ranking()
    await ptg()


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
    await (await Pt['Advcash']).update_from_dict({'parent': eb}).save()
    await (await Pt['CashDeposit']).update_from_dict({'parent': eb}).save()

if __name__ == "__main__":
    from loader import cns
    run(init())
