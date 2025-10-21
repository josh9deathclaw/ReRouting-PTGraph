import matplotlib.pyplot as plt
import networkx as nx
import pickle
import os

# Load graph
with open("data/processed/pt_graph.gpickle", "rb") as f:
    G = pickle.load(f)

# Position nodes based on lat/lon
pos = {n: (d['lon'], d['lat']) for n, d in G.nodes(data=True)}

# Define colors for each transport mode
mode_colors = {
    'train': 'blue',
    'tram': 'green',
    'bus': 'red'
}

# Create figure
plt.figure(figsize=(12, 12))
plt.axis('off')  # optional: remove axes

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=10, node_color='black', alpha=0.6)

# Draw edges by mode
for mode, color in mode_colors.items():
    edges = [(u, v) for u, v, d in G.edges(data=True) if d['mode'] == mode]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, alpha=0.4)

# Title
plt.title("Public Transport Network by Mode", fontsize=16)

# Save to file
output_path = os.path.join("data", "pt_network.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Graph saved as {output_path}")

# Show plot
plt.show()
