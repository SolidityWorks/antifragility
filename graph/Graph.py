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


class Graph:
    def __init__(self, nodes: [str, float, any, any], edges: [str, str, float, any]):  # node(id, size, ..), edge(from, to, weight, ..)
        self.cycles: {(str,): float} = {}
        # Set initial nodes values
        self.nodes: {str: Vertex} = {node[0]: Vertex(node[0]) for node in nodes}
        # Connect this nodes with edges
        [self.nodes[edge[0]].outs.append(Out(edge[1], edge[2])) for edge in edges]

    def find_cycle(self, visit: [bool], start: str, source: str, summ: float, cycle: (str,)):
        if visit[start]:
            if start == source and summ > 1.001:
                self.cycles[cycle] = summ
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

        return self.cycles

    def print_graph(self):
        for node in self.nodes.values():
            print(f"\nVertex {node.id}: ", end="")
            for out in node.outs:
                print(f"{out.to}[{out.weight}]", end=" ")
        print('')
