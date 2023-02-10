from asyncio import run

from clients.binance_с2с import get_my_ads
from db.models import Ad, Pair, Pt, User, Cur
from db.user import get_bc2c_users


async def ad_proc(res: {}, pts: [(str,)] = None):
    for ad in res['data']:
        adv = ad['adv']
        pair_unq = {'coin_id': adv['asset'], 'cur_id': adv['fiatUnit'], 'sell': adv['tradeType'] != 'SELL', 'ex_id': 1}
        pair_upd = {'total': int(res['total']), 'fee': float(adv['commissionRate'])}
        # Pair
        if pair := await Pair.get_or_none(**pair_unq):
            if pair.total != pair_upd['total'] or pair.fee != pair_upd['fee']:
                await pair.update_from_dict(pair_upd).save()
        else:
            pair: Pair = await Pair.create(**pair_unq, **pair_upd)

        # Pt
        pts_new: {str} = set(pt['identifier'] for pt in adv['tradeMethods'])
        if pts:  # pts filter for cycle update
            if not (pts_new := pts_new & {pt[0] for pt in pts}):
                # print('WARNING! no payment types:', [pt['identifier'] for pt in adv['tradeMethods']])
                continue
        pts: {Pt} = set()

        # Ad
        idd = int(adv['advNo']) - 10 ** 19
        ad_upd = {'price': float(adv['price']), 'maxFiat': float(adv['dynamicMaxSingleTransAmount']), 'status': adv['advStatus'] or 0,
                  'minFiat': adv['minSingleTransAmount'], 'detail': adv['remarks'], 'autoMsg': adv['autoReplyMsg']}
        if adv['createTime']:
            ad_upd.update({'created_at': adv['createTime'], 'updated_at': adv['advUpdateTime']})

        ad_mod: int = 0
        # ad, cr = await Ad.update_or_create(ad_upd, id=idd)  # todo: maybe later refactor
        if ad := await Ad.get_or_none(id=idd).prefetch_related('pts'):
            pts_old: {str} = set(pt.name for pt in ad.pts)
            if ad.price != ad_upd['price'] or ad.maxFiat != ad_upd['maxFiat']:  # or ad.minFiat != ad_upd['minFiat']  # todo: separate diffs
                await ad.update_from_dict(ad_upd).save()
                ad_mod += 1
            if pts_old != pts_new:
                await ad.pts.clear()
                for pt in pts_new:
                    pto, cr = await Pt.get_or_create(name=pt)
                    pts.add(pto)
                    if cr:
                        await pto.curs.add(await Cur[adv['fiatUnit']])
                await ad.pts.add(*pts)
                ad_mod += 1

        else:
            # user for ad
            usr = res['data'][0]['advertiser']
            user, cr = await User.update_or_create({'nickName': usr['nickName'], 'ex_id': 1}, uid=usr['userNo'])
            ad: Ad = await Ad.create(id=idd, pair=pair, user=user, **ad_upd)

            # pts
            if not pts:  # todo: DRY
                for pt in pts_new:
                    pto, cr = await Pt.get_or_create(name=pt)
                    pts.add(pto)
                    if cr:
                        await pto.curs.add(await Cur[adv['fiatUnit']])
            await ad.pts.add(*pts)
            ad_mod += 3

        if ad_mod:
            print(f"{pair.id}: {pair} [{pair.total}] {ad.price} * ({ad.minFiat}-{ad.maxFiat}) :", *pts_new)
        return ad_mod
    return 0


async def my_ads_actualize():
    for user in await get_bc2c_users():
        res = await get_my_ads(user)
        for ad in res:
            pair = await Pair.get(coin=ad['asset'], cur=ad['fiatUnit'], sell=ad['tradeType'] == 'SELL')
            ap = {
                'pair': pair,
                'price': ad['price'],
                'minFiat': ad['minSingleTransAmount'],
                'maxFiat': ad['surplusAmount'],
                'user_id': user.id,
                'detail': ad['remarks'],
                'autoMsg': ad['autoReplyMsg'],
                'created_at': int(ad['createTime']/1000),
                'updated_at': int(ad['advUpdateTime']/1000),
                'status': ad['advStatus']
            }
            adv, cr = await Ad.update_or_create(ap, id=int(ad['advNo']) - 10 ** 19)
            await adv.pts.add(*[await Pt[a['identifier']] for a in ad['tradeMethods']])


if __name__ == "__main__":
    try:
        from loader import cns
        run(my_ads_actualize())
    except KeyboardInterrupt:
        print('Stopped.')
