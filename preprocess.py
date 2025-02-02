import json
import stanza

filter_attributes = ["cap", "body", "stem", "flesh", "gills", "tubes", "pores", "underside", "ring", "spores", "habitat"]

stanza.download('bg', processors='tokenize,lemma,pos')
nlp = stanza.Pipeline('bg', processors='tokenize,lemma,pos', download_method=None)

def preprocess_mushroom(mushroom):
    return {attribute:preprocess_text(mushroom[attribute]) for attribute in mushroom if attribute in filter_attributes}

def preprocess_text(text):
    doc = nlp(text)
    lemmas = []
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.pos in ["ADJ", "NOUN", "ADP", "VERB", "NUM"]:
                lemmas.append(word.lemma)

    return " ".join(lemmas)

with open("corpus/parsed_mushrooms_data.json", "r", encoding="utf-8") as file:
    mushrooms = json.load(file)
    preprocessed_mushrooms = [preprocess_mushroom(mushroom) for mushroom in mushrooms]

with open("corpus/preprocessed_mushrooms.json", "w", encoding="utf-8") as file:
    json.dump(preprocessed_mushrooms, file, ensure_ascii=False, indent=4)