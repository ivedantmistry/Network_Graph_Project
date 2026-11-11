# Methodology & Error Analysis: Computational Literature

## 1. Project Objective

This project aims to algorithmically construct accurate character network graphs from raw literature without relying on manual data sanitization or hardcoded character lists.

## 2. The Pipeline Design

- **The Sliding Window:** To establish baseline relationships, the engine utilizes a 15-word sliding window array. If two canonical entities co-occur within this index boundary, their interaction weight increases.
- **Syntactic Dialogue Extraction:** Proximity alone is insufficient for narrative accuracy. The engine parses the dependency tree of speech verbs (e.g., "whispered", "shouted") to identify the Nominal Subject (`nsubj`). Active dialogue results in a heavier edge weight (+5) than passive proximity (+1).

## 3. Error Analysis and Limitations

- **The "Project Gutenberg" Artifact:** Because the pipeline ingests raw `.txt` files without arbitrary filtering, legal boilerplate occasionally registers as `PROPN` entities. I chose to preserve this artifact to demonstrate the strict adherence to the model's statistical output.
- **Coreference Blindspots:** Currently, the engine relies heavily on explicit `PERSON` tags. Pronoun coreference (e.g., mapping "He" back to "Holmes") is the next scheduled architectural upgrade to increase relationship density.
