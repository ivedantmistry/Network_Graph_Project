import spacy
import networkx as nx

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
    doc = nlp(text)

    # Step 1: Extract all raw entity mentions and their token positions
    raw_characters = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            raw_characters.append(token.text)

    # Step 2: Build our name normalization map
    canonical_map = normalize_names(raw_characters)

    # Step 3: Extract positions using the normalized names
    characters = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            normalized_name = canonical_map[token.text]
            characters.append((normalized_name, token.i))

    # Step 4: Initialize NetworkX Graph
    G = nx.Graph()

    # Step 5: Apply Sliding Window to find co-occurrences
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


# Test data containing name variations ('Dr. Watson' vs 'Watson')
large_test_text = """
Sherlock Holmes sat quietly by the fireplace in Baker Street. Dr. Watson entered the room 
with a heavy coat. 'Holmes,' Watson said, 'the weather outside is dreadful.' 
Later that evening, Sherlock Holmes and Dr. Watson traveled by carriage to Scotland Yard. 
The inspector greeted them at the door. Watson immediately began taking notes 
while Holmes examined the clues.
"""

network = build_character_network(large_test_text, window_size=15)

print("=== NORMALIZED PIPELINE RESULTS ===")
print(f"Total Unique Canonical Characters Found: {network.number_of_nodes()}")
print(f"Total Unique Relationships Found: {network.number_of_edges()}\n")

print("Normalized Edge Weights:")
for u, v, data in network.edges(data=True):
    print(f" - {u} <---> {v}: Strength {data['weight']}")
