import pickle
import networkx as nx
import pandas as pd

with open('data/processed/pt_graph.gpickle', 'rb') as f:
    G = pickle.load(f)

# Find connected components
components = list(nx.connected_components(G))
print(f"Number of components: {len(components)}")

# Show size of each component
for i, comp in enumerate(sorted(components, key=len, reverse=True)):
    print(f"Component {i+1}: {len(comp)} nodes")
    if len(comp) < 10:  # Show small components
        nodes = pd.read_csv('data/processed/stops_cleaned.csv')
        for node_id in comp:
            node_data = nodes[nodes['station_id'] == node_id]
            if not node_data.empty:
                print(f"  - {node_data.iloc[0]['stop_name']}")