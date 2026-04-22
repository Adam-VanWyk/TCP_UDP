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

        self.network_mode = "medium"

        self.network_profiles = {
            "low": {"loss": 0.05, "latency": (0.5, 1.0)},
            "medium": {"loss": 0.15, "latency": (0.5, 2.0)},
            "high": {"loss": 0.30, "latency": (1.0, 3.0)}
        }

    def create_graph(self, num_nodes, edges):
        self.graph.clear()
        self.graph.add_nodes_from(range(num_nodes))
        self.graph.add_edges_from(edges)
        self.pos = nx.spring_layout(self.graph)
        self.queues = {node: [] for node in self.graph.nodes()}

        profile = self.network_profiles[self.network_mode]
        self.edge_latency = {}
        self.edge_loss = {}

        for u, v in self.graph.edges():
            latency = random.uniform(*profile["latency"])
            loss = profile["loss"]

            self.edge_latency[(u, v)] = latency
            self.edge_latency[(v, u)] = latency

            self.edge_loss[(u, v)] = loss
            self.edge_loss[(v, u)] = loss

    def set_network_mode(self, mode):
        if mode in self.network_profiles:
            self.network_mode = mode
            print(f"Switched to {mode} network condition")
            self.create_graph(len(self.graph.nodes()), list(self.graph.edges()))

    def get_neighbors(self, node):
        return list(self.graph.neighbors(node))
    