import folium
import networkx as nx
import pickle

with open("data/processed/pt_graph.gpickle", "rb") as f:
    G = pickle.load(f)

avg_lat = sum(nx.get_node_attributes(G, 'lat').values()) / G.number_of_nodes()
avg_lon = sum(nx.get_node_attributes(G, 'lon').values()) / G.number_of_nodes()
m = folium.Map(location=[avg_lat, avg_lon], zoom_start=11)

for u, v, data in G.edges(data=True):
    from_node = G.nodes[u]
    to_node = G.nodes[v]
    color = {'train': 'red', 'tram': 'green', 'bus': 'blue'}.get(data['mode'], 'gray')
    folium.PolyLine(
        [(from_node['lat'], from_node['lon']), (to_node['lat'], to_node['lon'])],
        color=color, weight=2, opacity=0.5
    ).add_to(m)

m.save("network_visual.html")
print("✅ Saved interactive map to network_visual.html")
