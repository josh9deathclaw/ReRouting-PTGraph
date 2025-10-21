import networkx as nx
import pickle
import pandas as pd

GRAPH_PATH = "data/processed/pt_graph.gpickle"

def main():
    # Load graph
    with open('data/processed/pt_graph.gpickle', 'rb') as f:
        G = pickle.load(f)
    print("Graph loaded!")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")

    # Identify connected nodes and isolated nodes
    connected_nodes = [n for n in G.nodes if G.degree(n) > 0]
    isolated_nodes = [n for n in G.nodes if G.degree(n) == 0]

    print(f"Number of connected nodes: {len(connected_nodes)}")
    print(f"Number of isolated nodes: {len(isolated_nodes)}")
    if isolated_nodes:
        print(f"Sample isolated nodes: {isolated_nodes[:10]}")

    # Choose two nodes to test shortest path
    if len(connected_nodes) < 2:
        print("Not enough connected nodes to test shortest path.")
        return

    start_node = connected_nodes[0]
    end_node = connected_nodes[-1]

    print(f"\nTesting shortest path from '{start_node}' to '{end_node}':")
    try:
        path = nx.shortest_path(G, source=start_node, target=end_node, weight='time')
        path_length = nx.shortest_path_length(G, source=start_node, target=end_node, weight='time')
        print(f"Shortest path ({len(path)} stops, total travel time {path_length}s):")
        print(" -> ".join(path))
    except nx.NetworkXNoPath:
        print("No path exists between the chosen nodes!")

    # Optional: let user try arbitrary nodes
    while True:
        inp = input("\nEnter two node IDs separated by a comma (or 'q' to quit): ").strip()
        if inp.lower() == 'q':
            break
        try:
            node1, node2 = [x.strip() for x in inp.split(",")]
            path = nx.shortest_path(G, source=node1, target=node2, weight='time')
            path_length = nx.shortest_path_length(G, source=node1, target=node2, weight='time')
            print(f"Shortest path ({len(path)} stops, total travel time {path_length}s):")
            print(" -> ".join(path))
        except nx.NetworkXNoPath:
            print("No path exists between these nodes!")
        except KeyError as e:
            print(f"Invalid node: {e}")

if __name__ == "__main__":
    main()
