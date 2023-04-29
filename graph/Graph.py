class Vertex:
    def __init__(self, v_id: str):
        self.id = v_id
        self.outs: [Out] = []


class Out:
    #  Vertices node key
    def __init__(self, idd: str, weight: float):
        #  Set value of node key
        self.to = idd
        self.weight = weight


def sfm(tup: tuple):  # start cycle from min
    tup = tup[:-1]
    i = tup.index(min(tup))
    return tup[i:] + tup[:i]


class Graph:
    def __init__(self, nodes: {str: [float, any, any]}, edges: {(str, str): (float, str)}):  # node{id: size, ..), edge{(from, to): (weight, ..))
        self.cycles: {(str,): float} = {}
        # Set initial nodes values
        self.nodes: {str: Vertex} = {node_key: Vertex(node_key) for node_key in nodes}
        # Connect this nodes with edges
        [self.nodes[key[0]].outs.append(Out(key[1], edge[0])) for key, edge in edges.items()]

    def find_cycle(self, visit: [bool], start: str, source: str, summ: float, cycle: (str,)):
        if visit[start]:
            if start == source and summ > 1:
                self.cycles[sfm(cycle)] = summ
            return

        # Here modified the value of visited node
        visit[start] = True
        for out in self.nodes[start].outs:
            #  Visit to next edge
            self.find_cycle(visit, out.to, source, summ * out.weight, cycle+(out.to,))

        #  Reset the value of visited node status
        visit[start] = False

    def negative_cycle(self):
        for node_key in self.nodes:  # only keys
            # Auxiliary array for store visiting node flags
            visit = {node_key: False for node_key in self.nodes}  # Set initial visited node status off
            # Check cycle from and to node "node_key" with initial zero weight
            self.find_cycle(visit, node_key, node_key, 1, (node_key,))

        return dict(sorted(self.cycles.items(), key=lambda x: x[1]))

    def print_graph(self):
        for node in self.nodes.values():
            print(f"\nVertex {node.id}: ", end="")
            for out in node.outs:
                print(f"{out.to}[{out.weight}]", end=" ")
        print('')
