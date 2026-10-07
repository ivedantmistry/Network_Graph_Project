import spacy
import networkx as nx
from pyvis.network import Network

nlp = spacy.load("en_core_web_sm")


def normalize_names(raw_names):
    """Sorts names by length and maps short variations to their canonical full name."""
    unique_names = list(set(raw_names))
    unique_names.sort(key=len, reverse=True)

    canonical_map = {}
    for name in unique_names:
        canonical_map[name] = name
        for canonical in set(canonical_map.values()):
            if name != canonical and name in canonical:
                canonical_map[name] = canonical
                break
    return canonical_map


def build_character_network(text, window_size=15):
    print(
        "Processing text through spaCy NLP model (this may take a moment for large files)..."
    )
    doc = nlp(text)

    print("Extracting character entities...")
    raw_characters = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            raw_characters.append(token.text)

    canonical_map = normalize_names(raw_characters)

    characters = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            normalized_name = canonical_map[token.text]
            characters.append((normalized_name, token.i))

    print(f"Found {len(characters)} total entity mentions. Building network graph...")
    G = nx.Graph()

    for i in range(len(characters)):
        for j in range(i + 1, len(characters)):
            char1, index1 = characters[i]
            char2, index2 = characters[j]

            distance = abs(index1 - index2)

            if distance <= window_size and char1 != char2:
                if G.has_edge(char1, char2):
                    G[char1][char2]["weight"] += 1
                else:
                    G.add_edge(char1, char2, weight=1)

    return G


# --- MAIN EXECUTION ---
filename = "book.txt"  # Make sure your downloaded .txt book has this name

try:
    print(f"Reading '{filename}'...")
    with open(filename, "r", encoding="utf-8") as file:
        book_text = file.read()

    # Optional: Slice the text if you want to test just the first 10,000 characters/words first
    # book_text = book_text[:50000]

    # Build the network graph with a sliding window of 15 words
    network = build_character_network(book_text, window_size=15)

    print("\n=== BOOK ANALYSIS RESULTS ===")
    print(f"Total Unique Canonical Characters Found: {network.number_of_nodes()}")
    print(f"Total Unique Relationships Found: {network.number_of_edges()}\n")

    print("Top Relationships by Interaction Strength:")
    # Sort edges by weight from highest to lowest to see the main duos
    sorted_edges = sorted(
        network.edges(data=True), key=lambda x: x[2]["weight"], reverse=True
    )
    for u, v, data in sorted_edges[:15]:  # Show top 15 connections
        print(f" - {u} <---> {v}: Strength {data['weight']}")

    # Generate PyVis interactive visualization file
    print("\nGenerating interactive visual graph HTML file...")
    net = Network(
        height="700px",
        width="100%",
        notebook=False,
        bgcolor="#222222",
        font_color="white",
    )
    net.from_nx(network)
    net.save_graph("book_network.html")
    print("Success! Open 'book_network.html' in your web browser to see your graph.")

except FileNotFoundError:
    print(
        f"Error: Could not find '{filename}'. Please download a book text file from Project Gutenberg and save it as 'book.txt' in this directory."
    )
