import networkx as nx
from pyvis.network import Network

# 1. Recreate our graph with the data we extracted
G = nx.Graph()
G.add_edge("Holmes", "Watson", weight=5)

# 2. Initialize PyVis network (interactive HTML graph)
net = Network(
    height="500px", width="100%", notebook=False, bgcolor="#222222", font_color="white"
)

# 3. Load the NetworkX graph into PyVis
net.from_nx(G)

# 4. Save it as an HTML file you can open in your browser
net.save_graph("index.html")
print("Visual graph generated! Open 'index.html' in your browser.")
