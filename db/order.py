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
        pair = await Pair.get(sell=sell, coin_id=d['asset'], cur_id=d['fiat'])
        ad = await Ad.create(id=aid, price=d['price'], maxFiat=d['totalPrice'], minFiat=d['totalPrice'], pair=pair, user=user)
        await ad.pts.add(*[await Pt[pt] for pt in ptsd.values()])

    pt: str = ptsd.get(d['selectedPayId'])

    if sell:  # I receive to this fiat
        fiat: Fiat = await Fiat.get_or_none(id=d['selectedPayId']) if d['selectedPayId'] else None
    else:
        if not (ptc := await Ptc.get_or_none(pt_id=pt, cur_id=d['fiat'])):  # I pay from this fiat. Search my fiat by pt
            if not len(ptsd):
                print(ptsd)
            else:
                if not (ptc := await Ptc.filter(pt_id__in=ptsd.values(), cur_id=d['fiat']).first()):
                    print(ptsd)  # only for debug
        if not (fiat := await Fiat.filter(ptc=ptc, user=user).first()):
            if not ptc:
                print(pt)
            pto: Pt = await ptc.pt
            if par := await pto.parent:
                children = await par.children
                in_group_ptcs = [await Ptc.get_or_none(pt=c, cur_id=d['fiat']) for c in children]
                if None in in_group_ptcs:
                    in_group_ptcs = list(filter(lambda x: x, in_group_ptcs))
                    print(par)
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
        'taker': (await User.get_or_create({'nickName': d[f'{tter}Nickname'], 'ex_id': 1}, uid=d[f'{tter}UserNo']))[0] if d['makerUserNo'] == user.uid else user,
        # 'arch': d['archived'],
        'status': d['orderStatus'],
        'created_at': int(d['createTime']/1000)
    }
