from asyncio import run

from clients.binance_с2с import get_my_ads
from db.models import Ad, Pair, Pt, User, Cur, Adpt
from db.user import get_bc2c_users


async def ad_proc(res: {}, pts: [(str,)] = None):

    async def pts_save():
        for pt in pts_new:
            pto, is_new = await Pt.get_or_create(name=pt)
            pts.add(pto)
            if is_new:  # bind cur for new pt
                await pto.curs.add(await Cur[adv['fiatUnit']])
        await ad.pts.add(*pts)

    for data in res['data']:
        adv = data['adv']
        pair_unq = {'coin_id': adv['asset'], 'cur_id': adv['fiatUnit'], 'sell': adv['tradeType'] != 'SELL', 'ex_id': 1}  # todo: unHardcode ex
        pair_upd = {'total': int(res['total']), 'fee': float(adv['commissionRate'])}
        # Pair
        pair, is_new = await Pair.update_or_create(pair_upd, **pair_unq)

        # Pt
        pts_new: {str} = set(pt['identifier'] for pt in adv['tradeMethods'])
        if pts:  # pts filter for cycle update
            if not (pts_new := pts_new & {pt[0] for pt in pts}):
                print('WARNING! no payment types:', [pt['identifier'] for pt in adv['tradeMethods']])
                continue
        pts: {Pt} = set()

        # Ad
        idd = int(adv['advNo']) - 10 ** 19
        ad_upd = {'price': float(adv['price']),
                  'maxFiat': float(adv['dynamicMaxSingleTransAmount']),
                  'status': adv['advStatus'] or 0,
                  'minFiat': adv['minSingleTransAmount'],
                  'detail': adv['remarks'],
                  'autoMsg': adv['autoReplyMsg']}
        if adv['createTime']:  # when 'createTime' is None, 'advUpdateTime' is None too. In that case we delegate to postgres timestamping this record
            ad_upd.update({'created_at': adv['createTime'], 'updated_at': adv['advUpdateTime']})

        ad_mod: int = 0  # 0: not changed, 1: changed, 2: created
        # ad, cr = await Ad.update_or_create(ad_upd, id=idd)  # todo: maybe later refactor
        if ad := await Ad.get_or_none(id=idd).prefetch_related('pts'):  # try to get this ad from db (with same id)
            pts_old: {str} = set(pt.name for pt in ad.pts)
            # price or limit changed?
            if ad.price != ad_upd['price'] or ad.maxFiat != ad_upd['maxFiat']:  # yes  # or ad.minFiat != ad_upd['minFiat']  # todo: separate diffs
                await ad.update_from_dict(ad_upd).save()
                ad_mod += 1  # mod_status="price/limit changed"
            # pts are changed?
            if pts_old != pts_new:  # yes
                await ad.pts.clear()  # clean all pts in ad
                await pts_save()
                ad_mod += 2  # mod_status="pts changed" maybe + "price/limit changed"(1+2=3)
        else:  # no Ads with this id in db
            # user for ad
            usr = res['data'][0]['advertiser']
            user, cr = await User.update_or_create({'nickName': usr['nickName'], 'ex_id': 1}, uid=usr['userNo'])

            # check for old edges
            if edges := await Adpt.filter(ad__pair_id=pair.id, pt_id__in=pts_new).prefetch_related('ad__pts'):
                for edge in edges:
                    # if pair.coin_id == 'ETH' and edge.pt_id == 'TinkoffNew':
                    #     pass  # todo: remove the edge doubles
                    if len(edge.ad.pts) < 2:  # if this edge is only one in Ad,
                        ad_del = await edge.ad.delete()  # then delete whole Ad
                    else:
                        e_del = await edge.delete()  # else delete only this edge from old Ad
                # after todo: recording deleted edges for not updating next ads in cycle

            ad: Ad = await Ad.create(id=idd, pair=pair, user=user, **ad_upd)

            # pts
            await pts_save()
            ad_mod += 3

        if ad_mod:
            print(f"{pair.id}: {pair} [{pair.total}] {ad.price} * ({ad.minFiat}-{ad.maxFiat}) :", *pts_new)
            # await mod_graph(ad)

        return ad_mod
    return 0


# async def mod_graph(ad: Ad):
#     pair = ad.pair if type(ad.pair) is Pair else await ad.pair
#     for adpt in await ad.adpts:
#         ind0 = int(not pair.sell)
#         ind1 = int(pair.sell)
#         n = ['', '', adpt.pt_id]
#         n[ind0] = pair.coin_id
#         n[ind1] = pair.cur_id
#         edge, _ = await Edge.update_or_create({'adPt_id': adpt.id}, id='_'.join(n))


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
