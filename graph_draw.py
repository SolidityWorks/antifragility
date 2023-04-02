from asyncio import run

from db.models import Fiat, Asset, Cur, Coin, Adpt
from graph.Graph import Graph
from graph.Net import Net

net = Net(directed=True, height="1000")


async def graph():
    fiats: [Fiat] = await Fiat.filter(ptc__blocked=False, ptc__cur__blocked=False).prefetch_related('ptc__pt')
    # nodes (id, size, group, title)
    cur_rates = {cur.id: cur.rate for cur in await Cur.filter(blocked=False)}
    coin_rates = {coin.id: coin.rate for coin in await Coin.all()}
    # todo: grouping users
    cur_nodes: {str: [float, float, any]} = {}
    for fiat in fiats:
        node_name = f'{fiat.ptc.cur_id}_{fiat.ptc.pt.group or fiat.ptc.pt_id}'
        amount_in_usdt = fiat.amount/cur_rates[fiat.ptc.cur_id]
        if old_node := cur_nodes.get(node_name):  # grouping same nodes with summing amounts
            old_node[0] += amount_in_usdt
            old_node[1] += fiat.amount  # todo with target amount calc
        else:
            cur_nodes[node_name] = [amount_in_usdt, fiat.amount, 'cur']
    coin_nodes: {str: [float, float, any]} = {}  # the same signature as cur_nodes
    for asset in await Asset.all().prefetch_related('coin'):
        node_name = f'{asset.coin_id}_BinanceP2P'
        amount_in_usdt = (amount := asset.free + asset.freeze) * coin_rates[asset.coin_id] / cur_rates['RUB']
        if old_node := coin_nodes.get(node_name):
            old_node[0] += amount_in_usdt
            old_node[1] += asset.amount  # todo with target amount calc
        else:
            coin_nodes[node_name] = [amount_in_usdt, fiat.amount, 'coin']
    nodes = cur_nodes | coin_nodes
    net.add_nodes(nodes)
    # edges {(from, to): (weight, title)}
    edges: {(str, str): (float, str)} = {}
    for edge in await Adpt.filter(ad__status=0).prefetch_related('ad__pair__ex', 'pt'):
        ad = edge.ad
        price = ad.price
        nodes_0coin_1cur = (ad.pair.coin_id + '_' + ad.pair.ex.name,  # with merging RUB in found and fiat balances
                            ad.pair.cur_id + '_' + (edge.pt.group or edge.pt.name))
        nodes_key = nodes_0coin_1cur[int(not ad.pair.sell)], nodes_0coin_1cur[int(ad.pair.sell)]
        if not ad.pair.sell:
            price **= -1
        if old_edge := edges.get(nodes_key):
            if price > old_edge[0]:
                edges[nodes_key] = price, edge.pt.name
        else:
            edges[nodes_key] = price, edge.pt.name
    net.add_edges(edges)

    g = Graph(nodes, edges)
    g.print_graph()

    net.repulsion(200, 0.1, 100, 0.02, 0.1)
    net.set_template('graph/tmpl.html')

    net.show('graph/index.html')
    # net.show_buttons()

    cycles = sorted(g.negative_cycle().items(), key=lambda x: x[1], reverse=True)
    print(cycles)


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    run(graph())
