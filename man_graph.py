#    Print all negative cycles in directed graph
from __future__ import annotations


class AdjacencyEdge:
    #  Vertices node key
    def __init__(self, idd: int, weight: int | float):
        #  Set value of node key
        self.id: int = idd
        self.weight: float = weight
        self.next: AdjacencyEdge | None = None


class Vertex:
    def __init__(self, data: int):
        self.data: int = data
        self.next: AdjacencyEdge | None = None
        self.last: AdjacencyEdge | None = None


class Graph:
    def __init__(self, size: int):  # Number of Vertices
        if size:
            # Set initial nodes values
            self.nodes: [Vertex] = [Vertex(index) for index in range(size)]
            self.size: int = size
        else:
            raise Exception("Empty Graph")

    #   Handling the request of adding new edge
    def add_edge(self, start: int, last: int, weight: int | float):
        if 0 <= start < self.size and 0 <= last < self.size:
            edge = AdjacencyEdge(last, weight)
            if self.nodes[start].next is None:
                self.nodes[start].next = edge
            else:
                #  Add edge at the end
                self.nodes[start].last.next = edge

            #  Get last edge
            self.nodes[start].last = edge
        else:
            raise Exception("Invalid nodes")

    def print_graph(self):
        index = 0
        #  Print graph adjList Node value
        while index < self.size:
            print("\nAdjacency list of vertex ", index, " :", end="")
            edge = self.nodes[index].next
            while edge is not None:
                #  Display graph node
                print("  ", self.nodes[edge.id].data,
                      "[", edge.weight, "]", end="")
                #  Visit to next edge
                edge = edge.next

            index += 1

    def find_cycle(self, visit: [bool], start: int, source: int, summ: int | float, path: str):
        if visit[start]:
            if start == source and summ < 0:
                print("Path (", path, " ) = ", summ)

            return

        #  Here modified  the value of visited node
        visit[start] = True
        #  This is used to iterate nodes edges
        edge = self.nodes[start].next
        while edge is not None:
            self.find_cycle(visit, edge.id, source, summ + edge.weight, path + " → " + str(edge.id))
            #  Visit to next edge
            edge = edge.next

        #  Reset the value of visited node status
        visit[start] = False

    def negative_cycle(self):
        print("\nResult :")

        for i in range(self.size):
            # Auxiliary space which is used to store information about visited node
            # Set initial visited node status off
            visit = [False] * self.size

            #  Check cycle of node i to i
            #  Here initial cycle weight is zero
            self.find_cycle(visit, i, i, 0, " " + str(i))


def main():
    #  4 implies the number of nodes in graph
    g = Graph(4)
    #  Connect nodes with an edge
    g.add_edge(0, 1, -1)
    g.add_edge(0, 2, -2)
    g.add_edge(0, 3, -5)
    g.add_edge(1, 2, 1)
    g.add_edge(3, 2, 1.5)
    g.add_edge(2, 0, 1.2)
    #  Print graph element
    g.print_graph()
    #  Test
    g.negative_cycle()


if __name__ == "__main__":
    main()
