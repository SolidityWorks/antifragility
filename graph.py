from __future__ import annotations
from asyncio import run
import networkx as nx
from pyvis.network import Network
import numpy as np

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
                    # normalize_amounts = coin_amt*pair.coin.rate/rubusd_rate/10, cur_amt/pair.cur.rate/10
                    n0 = node[int(not pair.sell)]
                    nxg.add_node(n0, group=group[int(not pair.sell)], title=f'', label=f'{float(amounts[int(not pair.sell)]):.6}\n{n0}')  # , size=normalize_amounts[int(not pair.sell)]
                    n1 = node[int(pair.sell)]
                    nxg.add_node(n1, group=group[int(pair.sell)], title=f'', label=f'{float(amounts[int(pair.sell)]):.6}\n{n1}')  # , size=normalize_amounts[int(pair.sell)]

                    # rr = 100*pair.coin.rate/rubusd_rate, 100*ad.price/pair.cur.rate
                    # mod = (int(pair.sell)*2-1) * (rr[1] - rr[0])
                    nxg.add_edge(n0, n1, label=str(ad.price))  # , value=mod

                    cur_nodes[node[1]]['got'][pair.id] = True  # we need filling all PTs

            if False not in (cn['got'][pair.id] for cn in cur_nodes.values()):
                break  # all pts filled

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
