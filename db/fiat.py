from clients.binance_с2с import get_my_pts, balance, get_rates
from db.models import Ptc, Fiat, Pt, Asset, Cur
from db.user import get_bc2c_users

fiat_cur_map: {} = {
    # 357058112 user
    25842082: 'EUR',
    25812762: 'EUR',
    25416699: 'TRY',
    25303844: 'TRY',
    25303608: 'TRY',
    25236287: 'USD',
    25236248: 'USD',
    25236170: 'USD',
    25136929: 'TRY',
    24956898: 'RUB',
    24956617: 'RUB',
    24955395: 'TRY',
    24951855: 'RUB',
    24950350: 'TRY',
    20023779: 'RUB',
    17750004: 'RUB',
    17746529: 'EUR',
    17746495: 'USD',
    17746422: 'RUB',
    16026051: 'RUB',
    27973858: 'THB',
    # 464569741 user
    26650384: 'EUR',
    25369175: 'RUB',
    25369016: 'TRY',
    25368976: 'TRY',
    25368946: 'TRY',
    25368900: 'TRY',
    24078870: 'TRY',
    24078726: 'TRY',
    24078619: 'TRY',
    24078327: 'TRY',
    24075530: 'TRY',
    24054373: 'RUB',
    20450418: 'RUB',
    20450254: 'RUB',
    20450225: 'RUB',
    20450071: 'RUB',
    20449950: 'RUB',
    20405239: 'RUB',
    20376008: 'RUB',
}


async def upd_fiats():
    for user in await get_bc2c_users():
        my_pts = await get_my_pts(user)
        all_pts = await Pt.all().only('name').values_list('name', flat=True)
        if diffs := set([pt['identifier'] for pt in my_pts]) - set(all_pts):
            await Pt.bulk_create([Pt(name=diff) for diff in diffs])
        for pt in my_pts:
            dtl = pt['fields'][3 if pt['identifier'] == 'Advcash' else 1]['fieldValue']
            ptc, _ = await Ptc.get_or_create(pt_id=pt['identifier'])  # cur_id=fiat_cur_map[pt['id']],
            await Fiat.update_or_create({'user': user, 'ptc': ptc, 'detail': dtl}, id=pt['id'])
        await upd_fiat_rates()


async def upd_fiat_rates():
    r = await get_rates()
    for cur in await Cur.all():
        cur.rate = r[cur.id]
        await cur.save()


async def upd_founds():
    for user in await get_bc2c_users():
        for b in await balance(user):
            key = f'{b["asset"]}_{user.id}'
            d = {"coin_id": b["asset"],
                 "user": user,
                 "free": b["free"],
                 "freeze": b["freeze"],
                 "lock": b["locked"]}
            await Asset.update_or_create(d, id=key)
