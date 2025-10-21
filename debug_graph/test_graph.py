import pickle
import networkx as nx
from itertools import islice

# Load the graph
GRAPH_PATH = "data/processed/pt_graph.gpickle"

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

print(f"✅ Loaded graph: {GRAPH_PATH}")

# NetworkX 3.x replacement for nx.info(G)
print("Graph info:")
print(f"  Type: {type(G)}")
print(f"  Number of nodes: {G.number_of_nodes()}")
print(f"  Number of edges: {G.number_of_edges()}")
print(f"  Is directed: {G.is_directed()}")

# ------------------------------
# Test 1: Metadata sanity check
# ------------------------------
def test_node_metadata():
    print("\nTesting node metadata...")
    sample_nodes = list(islice(G.nodes(data=True), 5))
    for node_id, data in sample_nodes:
        assert 'stop_name' in data
        assert 'lat' in data
        assert 'lon' in data
        assert 'node_type' in data
    print("  ✓ Node metadata looks good")

def test_edge_metadata():
    print("\nTesting edge metadata...")
    sample_edges = list(islice(G.edges(data=True), 5))
    for u, v, data in sample_edges:
        assert 'mode' in data
        assert 'distance' in data
        assert 'time' in data
        assert 'emissions' in data
    print("  ✓ Edge metadata looks good")

# ------------------------------
# Test 2: Basic graph properties
# ------------------------------
def test_graph_connectivity():
    print("\nTesting connectivity...")
    connected = nx.is_connected(G)
    print(f"  Connected: {connected}")

def test_node_counts():
    print(f"\nNumber of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")

# ------------------------------
# Test 3: Pathfinding tests
# ------------------------------
def test_shortest_path_example():
    print("\nTesting shortest path between two sample stations...")
    # Pick two sample nodes
    nodes = list(G.nodes())
    start, end = nodes[0], nodes[-1]

    # Shortest distance path
    path = nx.shortest_path(G, source=start, target=end, weight='distance')
    total_distance = sum(G[u][v]['distance'] for u, v in zip(path[:-1], path[1:]))
    total_time = sum(G[u][v]['time'] for u, v in zip(path[:-1], path[1:]))
    total_emissions = sum(G[u][v]['emissions'] for u, v in zip(path[:-1], path[1:]))

    print(f"  Start: {G.nodes[start]['stop_name']}")
    print(f"  End: {G.nodes[end]['stop_name']}")
    print(f"  Path length: {len(path)} stops")
    print(f"  Total distance: {total_distance:.2f} m")
    print(f"  Total time: {total_time:.2f} s")
    print(f"  Total emissions: {total_emissions:.4f} kg CO2")


def test_shortest_path_example2():
    print("\nTesting shortest path between two sample stations...")
    nodes = list(G.nodes())

    # Try multiple random pairs until we find a connected pair
    import random
    for _ in range(10):
        start, end = random.sample(nodes, 2)
        try:
            path = nx.shortest_path(G, source=start, target=end, weight='distance')
            total_distance = sum(G[u][v]['distance'] for u, v in zip(path[:-1], path[1:]))
            total_time = sum(G[u][v]['time'] for u, v in zip(path[:-1], path[1:]))
            total_emissions = sum(G[u][v]['emissions'] for u, v in zip(path[:-1], path[1:]))

            print(f"  Start: {G.nodes[start]['stop_name']}")
            print(f"  End: {G.nodes[end]['stop_name']}")
            print(f"  Path length: {len(path)} stops")
            print(f"  Total distance: {total_distance:.2f} m")
            print(f"  Total time: {total_time:.2f} s")
            print(f"  Total emissions: {total_emissions:.4f} kg CO2")
            break  # stop after first successful path
        except nx.NetworkXNoPath:
            continue
    else:
        print("  ⚠️ Could not find a connected node pair for testing shortest path")

# ------------------------------
# Run all tests
# ------------------------------
if __name__ == "__main__":
    test_node_metadata()
    test_edge_metadata()
    test_graph_connectivity()
    test_node_counts()
    test_shortest_path_example2()
