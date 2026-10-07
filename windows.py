import spacy

nlp = spacy.load("en_core_web_sm")


def extract_interactions(text, window_size=15):
    doc = nlp(text)

    # Step 1: Find the array index of every PERSON in the text
    characters = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            # Save a tuple: (Character Name, Token Index)
            characters.append((token.text, token.i))

    print(f"Extracted Entities and their Positions: {characters}\n")

    interactions = []

    # Step 2: Compare every character against every other character
    for i in range(len(characters)):
        for j in range(i + 1, len(characters)):
            char1, index1 = characters[i]
            char2, index2 = characters[j]

            # Step 3: Calculate the distance between their index positions
            distance = abs(index1 - index2)

            # Step 4: If distance is less than or equal to window_size, it's a match
            if distance <= window_size:
                # We only want to record if they are different people
                if char1 != char2:
                    interactions.append((char1, char2))
                    print(f"Match: '{char1}' and '{char2}' are {distance} words apart.")


# Let's test it with a short paragraph
sample_text = """
Sherlock Holmes turned sharply to face Watson. 
He walked past the inspector and stared out the window. 
'We have a problem,' Holmes whispered to Watson.
"""

print(f"Testing with Window Size = 15")
print("-" * 30)
extract_interactions(sample_text, window_size=15)
