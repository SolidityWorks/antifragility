from pyvis.network import Network


class Net(Network):
    def add_nodes(self, nodes: dict, **kwargs):
        size_coefficient = .1
        for name, node in nodes.items():
            self.add_node(name, size=node[0]*size_coefficient, title=str(node[1]), group=node[2])  # , label='replace the id'

    def add_edges(self, edges: dict):
        for key, edge in edges.items():
            self.add_edge(key[0], key[1], label=f'{edge[0]:.6}', title=edge[1] or None, width=1)  # todo weight in proportion to relative profit
