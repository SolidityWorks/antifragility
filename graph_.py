from asyncio import run

from db.models import Fiat, Asset, Cur, Coin, Edge
from graph.Graph import Graph
from graph.Net import Net

# nodes
spot_quotable_coins = ['USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'USDC', 'TRY', 'EUR', 'RUB']


net = Net(directed=True, height="1000")


async def graph():
    fiats: [Fiat] = await Fiat.filter(ptc__blocked=False, ptc__cur__blocked=False).prefetch_related('ptc__pt')
    # nodes (id, size, group, title)
    cur_rates = {cur.id: cur.rate for cur in await Cur.filter(blocked=False)}
    coin_rates = {coin.id: coin.rate for coin in await Coin.all()}
    # todo: grouping users
    cur_nodes: [(str, float)] = [(f'{fiat.ptc.cur_id}_{fiat.ptc.pt.group or fiat.ptc.pt_id}', 10*fiat.amount/cur_rates[fiat.ptc.cur_id], 'cur', fiat.amount) for fiat in fiats]  # todo sum amount in groups
    coin_nodes: [(str, float)] = [(f'{a.coin_id}_BinanceP2P', 10*(amount := a.free + a.freeze)*coin_rates[a.coin_id]/cur_rates['RUB'], 'coin', amount) for a in await Asset.all().prefetch_related('coin')]  # todo: hardcode 'BinanceP2P'
    nodes = cur_nodes + coin_nodes  # todo: merge RUB in spot, found and fiat balances
    net.add_nodes(nodes)
    # edges (from, to, weight, title)
    edges = []
    for edge in await Edge.all().prefetch_related('adPt__ad__pair__ex', 'adPt__ad__pts'):
        ad = edge.adPt.ad
        pair = ad.pair
        for place in ad.pts:
            node = pair.coin_id + '_' + pair.ex.name, pair.cur_id + '_' + (place.group or place.name)
            ind0 = int(not pair.sell)
            ind1 = int(pair.sell)
            edges.append((node[ind0], node[ind1], ad.price, '1'))
    net.add_edges(edges)

    g = Graph(nodes, edges)
    g.print_graph()
    cycles = g.negative_cycle()
    print(cycles)

    net.repulsion(200, 0.1, 100, 0.02, 0.1)
    net.set_template('./tmpl.html')

    net.show('nx.html')
    net.show_buttons()


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    run(graph())
