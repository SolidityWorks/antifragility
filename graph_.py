from asyncio import run
from Net import Net
from man_graph import Graph

# nodes
spot_quotable_coins = ['USDT', 'BTC', 'BUSD', 'BNB', 'ETH', 'USDC', 'TRY', 'EUR', 'RUB']


net = Net(directed=True, height="1000")


async def graph():
    # nodes
    n = [
        ('zero', 2, 22, 0),
        ('one', 1, 11, 1),
        ('two', 1.2, 12, 0),
        ('three', 1.5, 15, 1),
    ]
    net.add_nodes(n)
    # edges
    e = [
        ('zero', 'one', -1, 222),
        ('zero', 'two', -2, 111),
        ('zero', 'three', -5, 122),
        ('one', 'two', 1, 155),
        ('three', 'two', 1.5, 543),
        ('two', 'zero', 1.2, 341),
    ]
    net.add_edges(e)

    g = Graph(n, e)
    cycles = g.negative_cycle()

    net.repulsion(200, 0.1, 100, 0.02, 0.1)
    net.set_template('./tmpl.html')

    net.show('nx.html')
    net.show_buttons()


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    from loader import cns
    run(graph())
