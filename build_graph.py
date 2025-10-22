import pandas as pd
import networkx as nx
import pickle

PROCESSED_DIR = "data/processed/"

EMISSIONS_FACTORS = {
    'train': 0.041,
    'tram': 0.045,
    'bus': 0.089
}

def build_graph(save=True):
    print("Building NetworkX graph...")
    
    # CHANGED: Use undirected graph (automatic bidirectional)
    G = nx.Graph()  # Changed from nx.DiGraph()
    
    # Load stations (nodes)
    stations = pd.read_csv(f'{PROCESSED_DIR}/stops_cleaned.csv')
    print(f"  Adding {len(stations)} nodes...")
    
    # Add nodes
    for _, station in stations.iterrows():
        # Create readable node ID
        station_id = station['station_id']
        mode_prefix = "pt"
        if "rail" in station_id:
            mode_prefix = "train"
        elif "tram" in station_id:
            mode_prefix = "tram"
        elif "bus" in station_id:
            mode_prefix = "bus"

        node_id = f"{mode_prefix}_{station_id}"

        G.add_node(
            node_id,
            stop_name=station['stop_name'],
            lat=station['stop_lat'],
            lon=station['stop_lon'],
            node_type='pt_stop',
            mode=mode_prefix
        )
    
    print(f"  ✓ Added {G.number_of_nodes()} nodes")
    
    # Load edges
    edges = pd.read_csv(f'{PROCESSED_DIR}/edges_merged.csv')
    print(f"  Adding {len(edges)} edges...")
    
    for _, edge in edges.iterrows():
        def format_node(station_id):
            if "rail" in station_id:
                return f"train_{station_id}"
            elif "tram" in station_id:
                return f"tram_{station_id}"
            elif "bus" in station_id:
                return f"bus_{station_id}"
            else:
                return f"pt_{station_id}"

        from_node = format_node(edge['from_station'])
        to_node = format_node(edge['to_station'])

        emissions_factor = EMISSIONS_FACTORS.get(edge['mode'], 0.1)
        emissions = (edge['distance'] / 1000) * emissions_factor

        G.add_edge(
            from_node,
            to_node,
            route_id=edge['route_id'],
            route_name=edge['route_name'],
            mode=edge['mode'],
            distance=edge['distance'],
            time=edge['time'],
            emissions_factor=emissions_factor,
            emissions=emissions
        )
    
    print(f"  ✓ Added {G.number_of_edges()} edges")
    print(f"  Graph is now {'CONNECTED' if nx.is_connected(G) else 'DISCONNECTED'}")
    
    # Save graph
    if save:
        output_path = f'{PROCESSED_DIR}/pt_graph.gpickle'
        with open(output_path, 'wb') as f:
            pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
        
        print(f"\n✓ Graph saved to {output_path}")
    
    return G

if __name__ == "__main__":
    build_graph()