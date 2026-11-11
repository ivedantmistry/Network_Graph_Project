# Character Network Extractor (NLP)

A computational linguistics pipeline that extracts character interaction networks from raw, unstructured literary texts.

## Technical Architecture

- **Entity Extraction:** `spaCy` (en_core_web_sm)
- **Graph Mathematics:** `NetworkX`
- **Visualization:** `PyVis` / `Vis.js`

## Current Capabilities

1. **Named Entity Normalization:** Dynamically maps character aliases (e.g., "Dr. Watson" and "Watson") to canonical nodes.
2. **Proximity Extraction:** Utilizes a configurable token-index sliding window to measure spatial co-occurrence between entities.
3. **Dialogue Attribution (In Progress):** Traverses dependency syntax trees (`nsubj`, `pobj`) to identify active speakers and listeners.

## How to Run locally

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python3 run_book.py`
