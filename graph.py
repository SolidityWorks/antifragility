from asyncio import run
import networkx as nx
from pyvis.network import Network
import numpy as np

from db.models import Pair, Cur, Ptc, Fiat, Asset

# nodes
spot_quotable_coins = ['USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'USDC', 'TRY', 'EUR', 'RUB']


async def graph():
    fiats: [Fiat] = await Fiat.filter(ptc__blocked=False, ptc__cur__blocked=False).prefetch_related('ptc__pt')
    curs: {str: (float, float)} = {
        f'{fiat.ptc.cur_id}_{fiat.ptc.pt.group or fiat.ptc.pt_id}': (fiat.amount, fiat.target)
        for fiat in fiats}
    coins: {str: (float, float)} = {a.coin_id: (a.free + a.freeze, a.target, a.coin.quotable) for a in await Asset.all().prefetch_related('coin')}

    # edges
    nxg = nx.DiGraph()
    for pair in await Pair.filter(cur__blocked=False).prefetch_related('ex', 'coin__assets', 'cur__ptcs__fiats', 'cur__ptcs__pt').all():
        ad = await pair.ads.order_by('-updated_at').limit(1).prefetch_related('pts').first()
        for place in {pt.group or pt.name for pt in ad.pts}:  # todo if place is group - make amount is sum of all children
            group = pair.ex.name, pair.cur_id
            node = pair.coin_id+'_'+pair.ex.name, pair.cur_id+'_'+place
            fiat_amount = sum(sum(f.amount for f in ptc.fiats) for ptc in pair.cur.ptcs if ptc.pt in ad.pts)
            amount = sum(a.free+a.freeze for a in pair.coin.assets)/1000, fiat_amount/1000
            n0 = node[int(not pair.sell)]
            nxg.add_node(n0, group=group[int(not pair.sell)], size=amount[int(not pair.sell)])
            n1 = node[int(pair.sell)]
            nxg.add_node(n1, group=group[int(pair.sell)], size=amount[int(not pair.sell)])

            nxg.add_edge(n0, n1, title=ad.price)

    net = Network(directed=True, height="1000")
    net.repulsion(200, 0, 200, 0.02, 0.1)
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
