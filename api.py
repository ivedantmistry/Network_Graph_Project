from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import networkx as nx

app = FastAPI()

# Allow your website frontend to communicate with this local API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")


class TextInput(BaseModel):
    text: str
    window_size: int = 15


@app.post("/api/analyze")
def analyze_text(data: TextInput):
    doc = nlp(data.text)

    # 1. Extract raw characters
    raw_characters = [token.text for token in doc if token.ent_type_ == "PERSON"]

    # 2. Simple canonical mapping
    unique_names = list(set(raw_characters))
    unique_names.sort(key=len, reverse=True)
    canonical_map = {name: name for name in unique_names}
    for name in unique_names:
        for canonical in set(canonical_map.values()):
            if name != canonical and name in canonical:
                canonical_map[name] = canonical
                break

    # 3. Get positions
    characters = [
        (canonical_map[token.text], token.i)
        for token in doc
        if token.ent_type_ == "PERSON"
    ]

    # 4. Build graph
    G = nx.Graph()
    for i in range(len(characters)):
        for j in range(i + 1, len(characters)):
            char1, index1 = characters[i]
            char2, index2 = characters[j]
            if abs(index1 - index2) <= data.window_size and char1 != char2:
                if G.has_edge(char1, char2):
                    G[char1][char2]["weight"] += 1
                else:
                    G.add_edge(char1, char2, weight=1)

    # Format output for frontend JSON
    nodes = [{"id": node} for node in G.nodes()]
    edges = [
        {"source": u, "target": v, "weight": d["weight"]}
        for u, v, d in G.edges(data=True)
    ]

    return {"nodes": nodes, "edges": edges}
