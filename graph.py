import networkx as nx

# The raw interactions your sliding window script just produced
interactions = [("Holmes", "Watson"), ("Holmes", "Watson")]

# Step 1: Initialize an empty Undirected Graph
G = nx.Graph()

# Step 2: Loop through the interactions and build the network
for char1, char2 in interactions:

    # Check if a connection already exists between these two characters
    if G.has_edge(char1, char2):
        # If yes, increase the strength (weight) of their relationship
        G[char1][char2]["weight"] += 1
    else:
        # If no, create a brand new edge with a starting weight of 1
        G.add_edge(char1, char2, weight=1)

# Step 3: Inspect the mathematical structure of the graph
print("--- GRAPH NODES (CHARACTERS) ---")
print(G.nodes())

print("\n--- GRAPH EDGES (RELATIONSHIPS) ---")
for node1, node2, data in G.edges(data=True):
    print(f"{node1} <---> {node2} | Interaction Strength (Weight): {data['weight']}")
