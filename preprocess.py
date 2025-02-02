import re
import stanza

filter_attributes = ["cap", "body", "stem", "flesh", "gills", "tubes", "pores", "underside", "ring", "spores", "habitat"]

stanza.download('bg', processors='tokenize,lemma, pos', verbose=False)
nlp = stanza.Pipeline('bg', processors='tokenize,lemma, pos', download_method=None, verbose=False)

def preprocess_mushrooms(mushrooms):    
    return [preprocess_mushroom(mushroom) for mushroom in mushrooms]

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
