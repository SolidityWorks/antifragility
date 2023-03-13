from asyncio import run
from tortoise import Tortoise

from clients.binance_с2с import get_ads
from db.ad import ad_proc
from db.models import Cur, Coin, Pt, Ptc, Ex, ExType


async def init():
    await Tortoise.generate_schemas()
    await cns[0].execute_script('''
CREATE FUNCTION price_upd() returns trigger as
$$
BEGIN
    PERFORM pg_notify('pc', row_to_json(NEW)::varchar);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
CREATE TRIGGER price_upd AFTER UPDATE OR INSERT ON ad
    FOR EACH ROW EXECUTE PROCEDURE price_upd();
    ''')

    await Coin.bulk_create(Coin(id=c, quotable=q) for c, q in {
        "USDT": True,
        "BTC": True,
        "ETH": True,
        "BNB": True,
        "BUSD": True,
        "RUB": True,
        "ADA": False,
        "SHIB": False,
        "MATIC": False,
        "XRP": False,
        "SOL": False,
        "DOT": False,
        "ICP": False,

        # "EUR": False,
        # "TRY": False,

        # # No p2p but /RUB
        # "ICP": False,
        # "LTC": False,
        # "WAVES": False,
        # "NEAR": False,
        # "ALGO": False,
        # "FTM": False,
        # "NEO": False,
        # "ALGO": False,
        # "ARPA": False,
        # "TRU": False,
        # "NU": False,
        # # No /RUB but p2p
        # "DOGE": False,
        # "DAI": False,
        # "TRX": False,
        # "GMT": False,
        # "WRX": False,
    }.items())
    await Cur.bulk_create(Cur(id=c, blocked=b) for c, b in {
        "RUB": False,
        "USD": True,
        "EUR": True,
        "TRY": True,
        "THB": False,
        # "AED": False,
        # "KZT": False,
        # "UZS": False,
        # "UAH": False,
    }.items())
    await Ex.create(name="bn", type=ExType.main)
    # actual payment types seeding
    await seed_pts(1, 2)  # lo-o-ong time
    await pt_ranking()
    await ptg()


async def seed_pts(start_page: int = 1, end_page: int = 5, curs: [] = None):
    i = 0
    for isSell in [0, 1]:
        for cur in curs or await Cur().all().prefetch_related('pts'):
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
    rb = 'RussianBanks'
    await (await Pt['RosBankNew']).update_from_dict({'group': rb}).save()
    await (await Pt['TinkoffNew']).update_from_dict({'group': rb}).save()
    await (await Pt['RaiffeisenBank']).update_from_dict({'group': rb}).save()
    await (await Pt['PostBankNew']).update_from_dict({'group': rb}).save()
    await (await Pt['UralsibBank']).update_from_dict({'group': rb}).save()
    await (await Pt['HomeCreditBank']).update_from_dict({'group': rb}).save()
    await (await Pt['MTSBank']).update_from_dict({'group': rb}).save()
    await (await Pt['AkBarsBank']).update_from_dict({'group': rb}).save()
    await (await Pt['UniCreditRussia']).update_from_dict({'group': rb}).save()
    await (await Pt['OTPBankRussia']).update_from_dict({'group': rb}).save()
    await (await Pt['RussianStandardBank']).update_from_dict({'group': rb}).save()
    await (await Pt['BCSBank']).update_from_dict({'group': rb}).save()
    await (await Pt['BankSaintPetersburg']).update_from_dict({'group': rb}).save()
    await (await Pt.get_or_create(name='CitibankRussia'))[0].update_from_dict({'group': rb}).save()
    await (await Pt.get_or_create(name='CreditEuropeBank'))[0].update_from_dict({'group': rb}).save()
    await (await Pt.get_or_create(name='RenaissanceCredit'))[0].update_from_dict({'group': rb}).save()
    await (await Pt.get_or_create(name='ABank'))[0].update_from_dict({'group': rb}).save()  # alfa analog
    b, _ = await Pt.get_or_create(name='BANK')  # BankTransfer (only for THB)
    bp, _ = await Ptc.get_or_create(pt=b, cur_id='RUB')
    bp.blocked = True
    await bp.save()
    sbp = await Pt.create(name='SBP', rank=-5, group=rb)
    await Ptc.create(pt=sbp, blocked=True, cur_id='RUB')
    sbr = await Pt.create(name='Sberbank', rank=-5, group=rb)
    await Ptc.create(pt=sbr, blocked=True, cur_id='RUB')
    vtb = await Pt.create(name='VTBBank', rank=-5, group=rb)
    await Ptc.create(pt=vtb, blocked=True, cur_id='RUB')
    otkr = await Pt.create(name='OtkritieBank', rank=-5, group=rb)
    await Ptc.create(pt=otkr, blocked=True, cur_id='RUB')
    svk = await Pt.create(name='SovkomBank', rank=-5, group=rb)
    await Ptc.create(pt=svk, blocked=True, cur_id='RUB')
    alf = await Pt.create(name='AlfaBank', rank=-5, group=rb)
    await Ptc.create(pt=alf, blocked=True, cur_id='RUB')
    await Ptc.create(pt_id='CashDeposit', blocked=True, cur_id='RUB')
    cip, _ = await Pt.get_or_create(name='CashInPerson')
    await (await Ptc.update_or_create(pt=cip, cur_id='RUB'))[0].update_from_dict({'blocked': True})
    await Ptc.create(pt_id='ABank', blocked=True, cur_id='RUB')
    await Ptc.get_or_create(pt_id='KoronaPay', cur_id='TRY')  # hack for old orders

    tb = 'TurkBanks'
    await (await Pt['Akbank']).update_from_dict({'group': tb}).save()
    await (await Pt['alBaraka']).update_from_dict({'group': tb}).save()
    await (await Pt['SpecificBank']).update_from_dict({'group': tb}).save()
    await (await Pt['HALKBANK']).update_from_dict({'group': tb}).save()
    await (await Pt['Fibabanka']).update_from_dict({'group': tb}).save()
    await (await Pt['BAKAIBANK']).update_from_dict({'group': tb}).save()
    await (await Pt['KuveytTurk']).update_from_dict({'group': tb}).save()
    await (await Pt['Ziraat']).update_from_dict({'group': tb}).save()
    await (await Pt['BanktransferTurkey']).update_from_dict({'group': tb}).save()
    # await (await Pt['BANK']).update_from_dict({'group': tb}).save() multiple currencies
    await (await Pt['VakifBank']).update_from_dict({'group': tb}).save()
    await (await Pt['Papara']).update_from_dict({'group': tb}).save()
    await (await Pt['QNB']).update_from_dict({'group': tb}).save()
    await (await Pt['ISBANK']).update_from_dict({'group': tb}).save()
    await (await Pt['Garanti']).update_from_dict({'group': tb}).save()
    await (await Pt['DenizBank']).update_from_dict({'group': tb}).save()
    await (await Pt.get_or_create(name='Fibabanka'))[0].update_from_dict({'group': tb}).save()
    #
    eb = 'EuroBanks'
    await (await Pt['SEPA']).update_from_dict({'group': eb}).save()
    await (await Pt['SEPAinstant']).update_from_dict({'group': eb}).save()
    await (await Pt['ING']).update_from_dict({'group': eb}).save()

    # ub = 'UkrBanks'
    # await (await Pt['RaiffeisenBankAval']).update_from_dict({'group': ub}).save()


if __name__ == "__main__":
    from loader import cns
    run(init())
