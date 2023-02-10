from asyncio import run, sleep

from tortoise.expressions import Q

from clients.binance_с2с import get_ads
from db.models import Pair, Fiat, Pt
from db.ad import ad_proc
from db.user import get_bc2c_users

sql = """
(select fiat.id, amount, target, user_id, cur_id, pt_id, "group", amount - target as need, (amount - target) / rate as need_usd
 from fiat
          inner join ptc p on p.id = fiat.ptc_id
          inner join cur c on c.id = p.cur_id
          inner join pt p2 on p2.name = p.pt_id
 where target is not null
   and (amount - target) / rate < 0
 order by need_usd)
UNION ALL
(select fiat.id, amount, target, user_id, cur_id, pt_id, "group", amount - target as need, (amount - target) / rate as need_usd
 from fiat
          inner join ptc p on p.id = fiat.ptc_id
          inner join cur c on c.id = p.cur_id
          inner join pt p2 on p2.name = p.pt_id
 where target is null
 order by amount / rate)
UNION ALL
(select fiat.id, amount, target, user_id, cur_id, pt_id, "group", amount - target as need, (amount - target) / rate as need_usd
 from fiat
          inner join ptc p on p.id = fiat.ptc_id
          inner join cur c on c.id = p.cur_id
          inner join pt p2 on p2.name = p.pt_id
 where target is not null
   and (amount - target) / rate > 0
 order by need_usd)
"""


async def cycle():
    if users := await get_bc2c_users(['ex']):
        pairs: [Pair] = [pair for pair in await users[0].ex.pairs if not (await pair.cur).blocked]
        while True:
            await tick(pairs)
            await sleep(1)

asci_map = [u"\u2591", u"\u2592", u"\u2593", u"\u2588"]


async def tick(pairs: [Pair]):
    cnt = 0
    suc, err, lp = 0, 0, len(pairs)
    fiats = await cns[0].execute_query_dict(sql)
    fd = {}
    for fiat in fiats:
        fd[fiat['cur_id']] = fd.get(fiat['cur_id'], []) + [(fiat['pt_id'], fiat['need'], fiat['group'], fiat['user_id'])]
    for pair in pairs:
        pts = [fiat for fiat in fd[pair.cur_id] if fiat[1] is None or fiat[1]*(int(pair.sell)*2-1) > 0]
        if not pair.sell:  # add in-group pts only for buy
            pt_groups = {pt[2] for pt in pts if pt[2]}
            pts += [(pt.name, None, pt.group) for pt in await Pt.filter(group__in=pt_groups)]
        if (res := await get_ads(pair.coin_id, pair.cur_id, pair.sell, [pt[0] for pt in pts])).get('data'):  # if isSell else [pt.name for pt in pts])
            ad_mod = await ad_proc(res, pts)
            suc += 1
            # just process indicate:
            print('[', end='')
            for x in range(suc + err):
                print(asci_map[ad_mod], end='')
            for x in range(lp - suc - err):
                print("_", end='')
            print(']', end='\r')
            cnt = (cnt + 1) % 4
        else:
            pair.total = 0
            await pair.save()
            err += 1
            print(f'NO Ads for pair {pair.id}: {pair}')
    print(f'\nSuccess: {suc}, Error: {err}, All: {lp}\n')
    await sleep(1)


if __name__ == "__main__":
    try:
        from loader import cns
        run(cycle())
    except KeyboardInterrupt:
        print('Stopped.')
