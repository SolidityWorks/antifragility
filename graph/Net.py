from pyvis.network import Network


class Net(Network):
    def add_nodes(self, nodes, **kwargs):
        for node in nodes:
            self.add_node(node[0], size=node[1]*.01, group=node[2], title=str(node[3]))  # , label='replace the id'

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge[0], edge[1], label=f'{edge[2]:.6}', title=edge[3] or None, width=2)  # todo weight in proportion to relative profit
