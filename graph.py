# Class for graph management from networkx

import networkx as nx 
import random

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.pos = {}
        self.stats = {
            "sent": 0,
            "delivered": 0,
            "dropped": 0
        }

    def create_graph(self, num_nodes, edges):
        self.graph.clear()
        self.graph.add_nodes_from(range(num_nodes))
        self.graph.add_edges_from(edges)
        self.pos = nx.spring_layout(self.graph)
        self.queues = {node: [] for node in self.graph.nodes()}

        self.edge_latency = {}

        for u, v in self.graph.edges():
            latency = random.uniform(0.5, 2.0)
            self.edge_latency[(u, v)] = latency
            self.edge_latency[(v, u)] = latency

        self.edge_loss = {}
        for u, v in self.graph.edges():
            loss = random.uniform(0.0, 0.3)
            self.edge_loss[(u, v)] = loss
            self.edge_loss[(v, u)] = loss

    def get_neighbors(self, node):
        return list(self.graph.neighbors(node))
    