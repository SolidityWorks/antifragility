from __future__ import annotations
from asyncio import run
from math import log

import networkx as nx
from networkx import NetworkXError
from pyvis.network import Network

from db.models import Pair, Cur, Ptc, Fiat, Asset, Pt

# nodes
spot_quotable_coins = ['USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'USDC', 'TRY', 'EUR', 'RUB']


async def graph():
    rubusd_rate = (await Cur['RUB']).rate
    groups = await Pt.filter(group__isnull=None).distinct().values_list('group', flat=True)
    fiats: [Fiat] = await Fiat.filter(ptc__blocked=False, ptc__cur__blocked=False).prefetch_related('ptc__pt')
    cur_nodes: {str: (float, float)} = {f'{fiat.ptc.cur_id}_{fiat.ptc.pt.group or fiat.ptc.pt_id}': {
        'amount': fiat.amount,
        'target': fiat.target,
        'got': {}
    } for fiat in fiats}
    coin_nodes: {str: {str: float | bool}} = {a.coin_id: {
        'amount': a.free + a.freeze,
        'target': a.target,
        'quotable': a.coin.quotable,
    } for a in await Asset.all().prefetch_related('coin')}

    # edges
    nxg = nx.DiGraph()
    for pair in await Pair.filter(cur__blocked=False).prefetch_related('ex', 'cur__ptcs', 'coin__assets').all():
        for cn in cur_nodes.values():
            cn['got'][pair.id] = cn['got'].get(pair.id, False)
        for ad in await pair.ads.order_by('-updated_at').limit(10).prefetch_related('pts').all():
            ad_pts = {pt.group or pt.name for pt in ad.pts}
            my_pts = {f.ptc.pt_id for f in fiats if f.ptc.cur_id == pair.cur_id}
            for place in ad_pts & my_pts:  # todo if place is group - make amount is sum of all children
                node = pair.coin_id + '_' + pair.ex.name, pair.cur_id + '_' + place
                if not cur_nodes[node[1]]['got'].get(pair.id):
                    group = pair.ex.name, pair.cur_id
                    cur_amt = sum(f.amount for f in await Fiat.filter(ptc__pt__group=place).all()) if place in groups else (await Fiat.get(ptc__pt_id=place, ptc_id__in=(ptc.id for ptc in pair.cur.ptcs))).amount  # TODO add user filtering
                    coin_amt = sum(a.free+a.freeze for a in pair.coin.assets)
                    amounts = coin_amt, cur_amt
                    ind0 = int(not pair.sell)
                    ind1 = int(pair.sell)
                    n0 = node[ind0]
                    # normalize_amounts = coin_amt*pair.coin.rate/rubusd_rate/10, cur_amt/pair.cur.rate/10
                    nxg.add_node(n0, group=group[ind0], label=f'{amounts[ind0]:.6}\n{n0}')  # title=,size=normalize_amounts[ind0]
                    n1 = node[ind1]
                    nxg.add_node(n1, group=group[ind1], label=f'{amounts[ind1]:.6}\n{n1}')  # title=,size=normalize_amounts[ind1]

                    # rr = 100*pair.coin.rate/rubusd_rate, 100*ad.price/pair.cur.rate
                    # mod = (ind1*2-1) * (rr[1] - rr[0])
                    weight = log(ad.price)*(2*ind0-1)
                    nxg.add_edge(n0, n1, value=weight, capacity=amounts[ind0], label=str(ad.price), title=f'{weight:.6}', weight=1)  # , value=mod

                    cur_nodes[node[1]]['got'][pair.id] = True  # we need filling all PTs

            if False not in (cn['got'][pair.id] for cn in cur_nodes.values()):
                break  # all pts filled

    try:
        if nc := nx.find_negative_cycle(nxg, 'USDT_bn', 'value'):
            print('FOUND NC:', nc)
        else:
            print('Errrrrrrorrrrrrr!!!!!!!!!!')
    except NetworkXError as e:
        print(e.args[0])

    net = Network(directed=True, height="1000")
    net.repulsion(200, 0, 200, 0.02, 0.1)
    net.set_template('./tmpl.html')
    # populates the nodes and edges data structures
    net.from_nx(nxg)
    net.show('nx.html')
    net.show_buttons()


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    run(graph())


# all_spot_quotable_currencies = ['USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'TUSD', 'PAX', 'USDC', 'XRP', 'TRX', 'NGN',
#                                 'TRY', 'EUR', 'ZAR', 'BKRW', 'IDRT', 'GBP', 'RUB', 'USDS', 'UAH', 'BIDR', 'AUD',
#                                 'DAI', 'BRL', 'BVND', 'VAI', 'USDP', 'DOGE', 'UST', 'DOT', 'PLN', 'RON']
