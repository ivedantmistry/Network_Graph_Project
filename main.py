# 1. Your raw extracted entities (with duplicates removed via a set)
raw_characters = list(
    set(["Sherlock Holmes", "Dr. Watson", "Watson", "Holmes", "Hudson", "Mrs. Hudson"])
)

# 2. Sort them by length, longest to shortest
# This ensures we establish the "full names" first before looking at single words.
raw_characters.sort(key=len, reverse=True)

# 3. Create a dictionary to hold our mapping
canonical_map = {}

for name in raw_characters:
    # Default assumption: the name is its own canonical ID
    canonical_map[name] = name

    # Check if this name is a piece of a longer, already-mapped name
    for canonical_name in set(canonical_map.values()):
        if name != canonical_name and name in canonical_name:
            # If "Watson" is inside "Dr. Watson", remap it
            canonical_map[name] = canonical_name
            break  # Stop looking once we find a match

# 4. Let's see the results!
print("--- CANONICAL MAPPING ---")
for raw_name, canonical_id in canonical_map.items():
    print(f"Raw String: '{raw_name:15}' -> Canonical Node: '{canonical_id}'")
