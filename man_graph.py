#    Print all negative cycles in directed graph
from __future__ import annotations


class AdjacencyEdge:
    #  Vertices node key
    def __init__(self, idd: str, weight: float):
        #  Set value of node key
        self.id = idd
        self.weight = weight
        self.next: AdjacencyEdge | None = None


class Vertex:
    def __init__(self, data: str):
        self.data = data
        self.next: AdjacencyEdge | None = None
        self.last: AdjacencyEdge | None = None


class Graph:
    def __init__(self, nodes: [str, float, any, any], edges: [str, str, float, any]):  # Number of Vertices
        self.cycles: {(str,): float} = {}
        # Set initial nodes values
        self.nodes: {str: Vertex} = {node[0]: Vertex(node[0]) for node in nodes}
        # Connect this nodes with edges
        [self.add_edge(*edge) for edge in edges]

    #   Handling the request of adding new edge
    def add_edge(self, start: str, last: str, weight: float, *attrs: None):
        edge = AdjacencyEdge(last, weight)
        if self.nodes[start].next:  # node already have outs
            self.nodes[start].last.next = edge  # Add edge at the end
        else:  # it's first out for this node
            self.nodes[start].next = edge
        # Write last edge
        self.nodes[start].last = edge

    def print_graph(self):
        #  Print graph adjList Node value
        for node, edge in self.nodes.items():
            print("\nAdjacency list of vertex ", node, " :", end="")
            next_edge = self.nodes[node].next
            while next_edge is not None:
                #  Display graph node
                print("  ", self.nodes[next_edge.id].data, "[", next_edge.weight, "]", end="")
                #  Visit to next edge
                next_edge = next_edge.next

    def find_cycle(self, visit: [bool], start: str, source: str, summ: float, cycle: (str,)):
        if visit[start]:
            if start == source and summ < 0:
                self.cycles[cycle] = summ
            return

        #  Here modified  the value of visited node
        visit[start] = True
        #  This is used to iterate nodes edges
        edge = self.nodes[start].next
        while edge is not None:
            self.find_cycle(visit, edge.id, source, summ + edge.weight, cycle+(edge.id,))
            #  Visit to next edge
            edge = edge.next

        #  Reset the value of visited node status
        visit[start] = False

    def negative_cycle(self):
        for node_key in self.nodes:  # only keys
            # Auxiliary space which is used to store information about visited node
            # Set initial visited node status off
            visit = {node_key: False for node_key in self.nodes}

            #  Check cycle of node i to i
            #  Here initial cycle weight is zero
            self.find_cycle(visit, node_key, node_key, 0, (node_key,))

        return self.cycles


def main():
    g = Graph([])
    #  Print graph element
    g.print_graph()
    #  Test
    print("\n", g.negative_cycle())


if __name__ == "__main__":
    main()
