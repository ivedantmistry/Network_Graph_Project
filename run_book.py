import pickle
import re
from fastcoref import spacy_component
from fastcoref.modeling import FCorefModel
import networkx as nx
from pyvis.network import Network
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

_orig_batch_setitems = pickle._Pickler._batch_setitems
pickle._Pickler._batch_setitems = lambda self, items, obj=None: _orig_batch_setitems(
    self, items, obj
)
FCorefModel.all_tied_weights_keys = {}

print("Loading spaCy and Neural Coreference Models (this takes a moment)...")
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("fastcoref")


def clean_entity_text(text):
    """Normalizes whitespace and strips trailing possessives ('s)."""
    text = " ".join(text.split())
    return re.sub(r"(?:'s|’s)$", "", text).strip()


def normalize_names(raw_names):
    """Maps shorter name variations (e.g., 'Harry') to their canonical full name ('Harry Potter')."""
    unique_names = sorted(set(raw_names), key=len, reverse=True)

    canonical_map = {}
    for name in unique_names:
        canonical_map[name] = name
        pattern = re.compile(rf"\b{re.escape(name)}\b")
        for canonical in unique_names:
            if len(canonical) > len(name) and pattern.search(canonical):
                canonical_map[name] = canonical
                break
    return canonical_map


def extract_dialogue_interactions(doc, token_to_char):
    """
    Traverses the dependency tree to find active speakers and their listeners.
    Returns a list of tuples: (Canonical_Speaker, Canonical_Listener)
    """
    speech_verbs = {
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
    }
    dialogue_pairs = []

    for word in doc:
        if word.lemma_ in speech_verbs:
            speaker = None
            listener = None

            for child in word.children:
                if child.dep_ == "nsubj" and child.i in token_to_char:
                    speaker = token_to_char[child.i]

                if child.dep_ in ("dative", "dobj") and child.i in token_to_char:
                    listener = token_to_char[child.i]

                if child.dep_ == "prep":
                    for grandchild in child.children:
                        if grandchild.dep_ == "pobj" and grandchild.i in token_to_char:
                            listener = token_to_char[grandchild.i]

            if speaker and listener and speaker != listener:
                dialogue_pairs.append((speaker, listener))

    return dialogue_pairs


def build_character_network(text, window_size=15):
    print("Running neural coreference resolution (mapping pronouns to names)...")
    raw_doc = nlp(text, component_cfg={"fastcoref": {"resolve_text": True}})
    resolved_text = raw_doc._.resolved_text

    print("Processing resolved text through standard NLP pipeline...")
    doc = nlp(resolved_text, disable=["fastcoref"])

    print("Extracting character entities...")
    person_ents = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            cleaned = clean_entity_text(ent.text)
            if len(cleaned) > 1:
                person_ents.append((cleaned, ent.start, ent.end))

    canonical_map = normalize_names([name for name, _, _ in person_ents])

    characters = []
    token_to_char = {}
    for cleaned, start, end in person_ents:
        canon_name = canonical_map[cleaned]
        characters.append((canon_name, start))
        for idx in range(start, end):
            token_to_char[idx] = canon_name

    print(
        f"Found {len(characters)} total entity mentions. Building baseline network graph..."
    )
    G = nx.Graph()

    for i in range(len(characters)):
        for j in range(i + 1, len(characters)):
            char1, index1 = characters[i]
            char2, index2 = characters[j]

            if abs(index1 - index2) <= window_size and char1 != char2:
                start_idx = min(index1, index2)
                end_idx = max(index1, index2)

                interaction_text = " ".join(
                    [token.text for token in doc[start_idx : end_idx + 1]]
                )
                sentiment_score = sia.polarity_scores(interaction_text)["compound"]

                edge_color = "#6b7280"
                if sentiment_score > 0.1:
                    edge_color = "#10b981"
                elif sentiment_score < -0.1:
                    edge_color = "#ef4444"

                if G.has_edge(char1, char2):
                    G[char1][char2]["weight"] += 1
                    current_sentiment = G[char1][char2].get("sentiment", 0)
                    new_sentiment = (current_sentiment + sentiment_score) / 2
                    G[char1][char2]["sentiment"] = new_sentiment

                    if new_sentiment > 0.1:
                        G[char1][char2]["color"] = "#10b981"
                    elif new_sentiment < -0.1:
                        G[char1][char2]["color"] = "#ef4444"
                    else:
                        G[char1][char2]["color"] = "#6b7280"
                else:
                    G.add_edge(
                        char1,
                        char2,
                        weight=1,
                        sentiment=sentiment_score,
                        color=edge_color,
                    )

    print("Hunting for active speaker-to-listener dialogue...")
    dialogue_interactions = extract_dialogue_interactions(doc, token_to_char)
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

    print("Slicing text to 10,000 characters for memory-safe neural processing...")
    book_text = book_text[:10000]

    network = build_character_network(book_text, window_size=15)

    print("\n=== BOOK ANALYSIS RESULTS ===")
    print(f"Total Unique Canonical Characters Found: {network.number_of_nodes()}")
    print(f"Total Unique Relationships Found: {network.number_of_edges()}\n")

    print("Top Relationships by Interaction Strength:")
    sorted_edges = sorted(
        network.edges(data=True), key=lambda x: x[2]["weight"], reverse=True
    )
    for u, v, data in sorted_edges[:15]:
        sentiment = data.get("sentiment", 0)
        mood = "Neutral"
        if sentiment > 0.1:
            mood = "Positive"
        elif sentiment < -0.1:
            mood = "Negative"

        print(
            f" - {u} <---> {v}: Strength {data['weight']} | Mood: {mood} ({sentiment:.2f})"
        )

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
