import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")

text = "Holmes quietly whispered to the inspector."
doc = nlp(text)

print("Server starting...")
print("Open your web browser and go to: http://localhost:5050")
print("Press Ctrl+C in this terminal to stop the server when you are done.")

# Added port=5050 to bypass the macOS AirPlay conflict
displacy.serve(doc, style="dep", port=5050)