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


def extract_dialogue_interactions(doc, canonical_map):
    """
    Traverses the dependency tree to find active speakers and their listeners.
    Returns a list of tuples: (Canonical_Speaker, Canonical_Listener)
    """
    speech_verbs = [
        "say",
        "whisper",
        "shout",
        "reply",
        "gasp",
        "mutter",
        "ask",
        "answer",
        "cry",
        "tell",
        "call",
    ]
    dialogue_pairs = []

    for word in doc:
        if word.lemma_ in speech_verbs:
            speaker = None
            listener = None

            for child in word.children:
                # Find the Speaker
                if child.dep_ == "nsubj" and child.ent_type_ == "PERSON":
                    speaker = child.text

                if child.dep_ in ["dative", "dobj"] and child.ent_type_ == "PERSON":
                    listener = child.text

                if child.dep_ == "prep":
                    for grandchild in child.children:
                        if (
                            grandchild.dep_ == "pobj"
                            and grandchild.ent_type_ == "PERSON"
                        ):
                            listener = grandchild.text

            if speaker and listener:
                if speaker in canonical_map and listener in canonical_map:
                    canon_speaker = canonical_map[speaker]
                    canon_listener = canonical_map[listener]

                    if canon_speaker != canon_listener:
                        dialogue_pairs.append((canon_speaker, canon_listener))

    return dialogue_pairs


def build_character_network(text, window_size=15):
    print(
        "Processing text through spaCy NLP model (this may take a moment for large files)..."
    )
    doc = nlp(text)

    print("Extracting character entities...")
    raw_characters = [token.text for token in doc if token.ent_type_ == "PERSON"]
    canonical_map = normalize_names(raw_characters)

    characters = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            normalized_name = canonical_map[token.text]
            characters.append((normalized_name, token.i))

    print(
        f"Found {len(characters)} total entity mentions. Building baseline network graph..."
    )
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

    print("Hunting for active speaker-to-listener dialogue...")
    dialogue_interactions = extract_dialogue_interactions(doc, canonical_map)
    print(
        f"Found {len(dialogue_interactions)} explicit conversations via syntax trees."
    )

    for speaker, listener in dialogue_interactions:
        if G.has_edge(speaker, listener):
            G[speaker][listener]["weight"] += 5
        else:
            G.add_edge(speaker, listener, weight=5)

    return G


filename = "book.txt"

try:
    print(f"Reading '{filename}'...")
    with open(filename, "r", encoding="utf-8") as file:
        book_text = file.read()

    network = build_character_network(book_text, window_size=15)

    print("\n=== BOOK ANALYSIS RESULTS ===")
    print(f"Total Unique Canonical Characters Found: {network.number_of_nodes()}")
    print(f"Total Unique Relationships Found: {network.number_of_edges()}\n")

    print("Top Relationships by Interaction Strength:")
    sorted_edges = sorted(
        network.edges(data=True), key=lambda x: x[2]["weight"], reverse=True
    )
    for u, v, data in sorted_edges[:15]:
        print(f" - {u} <---> {v}: Strength {data['weight']}")

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
    print(f"Error: Could not find '{filename}'.")
