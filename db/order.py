from __future__ import annotations

from clients.binance_с2с import get_ad
from db.models import Order, Ad, Fiat, Pair, Pt, Ptc, User


async def orders_proc(orders: [{}], user: User):
    for od in orders:  # todo: refact to bulk_create
        order = await ordr(od, user)
        if o := await Order.get_or_none(id=order['id']):
            await o.update_from_dict(order).save()
            print('', end=':')
        else:
            await Order.create(**order)
            print('', end='.')


async def ordr(d: {}, user: User):  # class helps to create ad object from input data
    if not user.uid:
        if d['buyerNickname'] == user.nickName:
            user.uid = d['buyerUserNo']
        elif d['sellerNickname'] == user.nickName:
            user.uid = d['sellerUserNo']
        await user.save()
    old_pts = {
        'Tinkoff': 'TinkoffNew',
        'RosBank': 'RosBankNew',
        'Sberbank': 'RosBankNew',
        'VTBBank': 'RosBankNew',
        'OtkritieBank': 'RosBankNew',
        'SovkomBank': 'RosBankNew',
        'YandexMoney': 'YandexMoneyNew',
        'PostBank': 'PostBankNew',
        'PostBankRussia': 'PostBankNew',
        'RaiffeisenBankRussia': 'RaiffeisenBank',
        'AlfaBank': 'ABank',
    }
    ptsd = {p['id']: old_pts.get(p['identifier'], p['identifier']) for p in d['payMethods']}

    aid: int = int(d['advNo']) - 10 ** 19
    sell: bool = d['tradeType'] == 'SELL'
    if not await Ad.exists(id=aid):
        if not (pair := await Pair.get_or_none(sell=sell, coin_id=d['asset'], cur_id=d['fiat'])):
            pass
        ap = {
            'id': aid,
            'pair': pair,
            'price': d['price'],
            'minFiat': d['totalPrice'],
            'maxFiat': d['totalPrice'],
            'created_at': int(d['createTime']/1000),
            'status': 9,
            'user': (await User.get_or_create({'nickName': d['makerNickname'], 'ex_id': 1}, uid=d[f'makerUserNo']))[0]
        }
        if add := await get_ad(d['advNo']):
            ap.update({
                'status': add['adv']['advStatus'],
                'created_at': int(add['adv']['createTime']/1000),
                'updated_at': int(add['adv']['advUpdateTime']/1000),
                'detail': add['adv']['remarks'],
                'autoMsg': add['adv']['autoReplyMsg'],
            })
        ad = await Ad.create(**ap)
        await ad.pts.add(*[await Pt[pt] for pt in ptsd.values()])

    pt: str = ptsd.get(d['selectedPayId'])

    if sell:  # I receive to this fiat
        fiat: Fiat | None = await Fiat.get_or_none(id=d['selectedPayId']) if d['selectedPayId'] else None
    else:
        fiat = None
        if not (ptc := await Ptc.get_or_none(pt_id=pt, cur_id=d['fiat'])):  # I pay from this fiat. Search my fiat by pt
            if not len(ptsd):
                print(ptsd)
            else:
                if not (ptc := await Ptc.filter(pt_id__in=ptsd.values(), cur_id=d['fiat']).first()):
                    pto: Pt = await Pt[pt]
                    if grp := pto.group:
                        siblings_pt_ids = await Pt.filter(group=grp).values_list('name', flat=True)
                        in_group_ptc_ids = await Ptc.filter(pt_id__in=siblings_pt_ids, cur_id=d['fiat']).values_list('id', flat=True)
                        fiat = await Fiat.filter(ptc_id__in=in_group_ptc_ids, user=user).first()
                    else:
                        print(ptsd)  # only for debug
        if not fiat and not (fiat := await Fiat.filter(ptc=ptc, user=user).first()):
            if not ptc:
                print(pt)
            pto: Pt = await ptc.pt
            if grp := pto.group:
                siblings_pt_ids = await Pt.filter(group=grp).values_list('name', flat=True)
                in_group_ptcs = await Ptc.filter(pt_id__in=siblings_pt_ids, cur_id=d['fiat']).all()
                # if None in in_group_ptcs:
                #     in_group_ptcs = list(filter(lambda x: x, in_group_ptcs))
                #     print(grp)
                fiat = await Fiat.filter(ptc_id__in=[pc.id for pc in in_group_ptcs], user=user).first()
            else:
                print(pto)
                fiat = None
    tter = "buyer" if d["tradeType"] == "SELL" else "seller"
    return {
        'id': int(d['orderNumber']) - 2*10**19,
        'ad_id': aid,
        'amount': float(d['amount']),
        'pt_id': pt,
        'fiat': fiat,
        'taker': (await User.get_or_create({'nickName': d[f'{tter}Nickname']}, uid=d[f'{tter}UserNo'], ex_id=1))[0] if d['makerUserNo'] == user.uid else user,
        # 'arch': d['archived'],
        'status': d['orderStatus'],
        'created_at': int(d['createTime']/1000),
        'notify_pay_at': int(d['notifyPayEndTime']/1000) if d['notifyPayEndTime'] else None,
        'confirm_pay_at': int(d['confirmPayEndTime']/1000) if d['confirmPayEndTime'] else None
    }
