from clients.binance_client import get_my_pts, balance
from db.models import Ptc, Fiat, Pt, Asset
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
    #  user
}


async def upd_fiats():
    for user in await get_bc2c_users():
        my_pts = await get_my_pts(user)
        all_pts = await Pt.all().only('name').values_list('name', flat=True)
        if diffs := set([pt['identifier'] for pt in my_pts]) - set(all_pts):
            await Pt.bulk_create([Pt(name=diff) for diff in diffs])
        for pt in my_pts:
            dtl = pt['fields'][3 if pt['identifier'] == 'Advcash' else 1]['fieldValue']
            ptc, _ = await Ptc.get_or_create(cur_id=fiat_cur_map[pt['id']], pt_id=pt['identifier'])
            await Fiat.update_or_create(id=pt['id'], user=user, ptc=ptc, detail=dtl)


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
