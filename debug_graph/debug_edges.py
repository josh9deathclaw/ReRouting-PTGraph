import networkx as nx
import pickle
import networkx as nx
import pandas as pd

# Load the saved graph
with open('data/processed/pt_graph.gpickle', 'rb') as f:
    G = pickle.load(f)

print("Graph loaded!")
print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")

# Nodes with at least one edge (connected)
connected_nodes = [n for n in G.nodes if G.degree[n] > 0]
print(f"Number of connected nodes: {len(connected_nodes)}")
print("Sample connected nodes:", connected_nodes[:10])

# Nodes with no edges (isolated)
isolated_nodes = list(nx.isolates(G))
print(f"Number of isolated nodes: {len(isolated_nodes)}")
print("Sample isolated nodes:", isolated_nodes[:10])

# Optional: print edges
print(f"Number of edges: {G.number_of_edges()}")
print("Sample edges:", list(G.edges(data=True))[:10])
