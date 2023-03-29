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
    def __init__(self, edges: [str, str, float]):  # Number of Vertices
        self.nodes: {str: Vertex} = {}
        self.cycles: {(str,): float} = {}
        if len(edges):
            # Set initial nodes values
            for edge in edges:
                if not self.nodes.get(edge[0]):
                    self.nodes[edge[0]] = Vertex(edge[0])
                if not self.nodes.get(edge[1]):
                    self.nodes[edge[1]] = Vertex(edge[1])
                self.add_edge(*edge)
        else:
            raise Exception("Empty Graph")

    #   Handling the request of adding new edge
    def add_edge(self, start: str, last: str, weight: float):
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
    g = Graph([
        ('zero', 'one', -1),
        ('zero', 'two', -2),
        ('zero', 'three', -5),
        ('one', 'two', 1),
        ('three', 'two', 1.5),
        ('two', 'zero', 1.2),
    ])
    #  Print graph element
    g.print_graph()
    #  Test
    print("\n", g.negative_cycle())


if __name__ == "__main__":
    main()
