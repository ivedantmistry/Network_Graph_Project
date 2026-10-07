import spacy

nlp = spacy.load("en_core_web_sm")


def find_speaker(text):
    doc = nlp(text)

    # We define the verbs that indicate someone is talking
    speech_verbs = ["say", "whisper", "shout", "reply", "gasp"]

    print(f"Analyzing sentence: {text}\n")

    # Step 1: Loop through every word in the sentence
    for word in doc:

        # Step 2: Check if the word is one of our speech verbs
        if word.lemma_ in speech_verbs:
            print(f"Target Verb Found: '{word.text}'")

            # Step 3: Look at the "children" of this verb in the syntax tree
            for child in word.children:

                # Step 4: If a child is tagged as the nominal subject (nsubj), that is our speaker
                if child.dep_ == "nsubj":
                    print(f"SUCCESS: The speaker is '{child.text}'")
                    return child.text

    print("No speaker found in this sentence.")
    return None


# Let's test your engine with three different sentence structures
find_speaker("'It is a trap,' shouted Watson.")
print("-" * 30)
find_speaker("Holmes quietly whispered to the inspector.")
print("-" * 30)
find_speaker("The door slammed shut.")
