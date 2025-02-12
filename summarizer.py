from sklearn.feature_extraction.text import CountVectorizer
import re
import nltk
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize, word_tokenize

def process_sentence(sentence): 
    stopPhrases = ["Снимки", "Снимка", "Върни се до горе", "редакция", "подготвиха", "галерия", "Автор на описанието"]
    if any(phrase in sentence for phrase in stopPhrases):
        return ""
    
    tokens = word_tokenize(sentence)
    if len(tokens) < 2:
        return "" # ignore sentences with less than 2 words, they will not be useful for summarization
    
    transformed_sentence = sentence
    first_word = tokens[0]
    second_word = tokens[1]
    rest_of_sentence = sentence[len(first_word):].strip() 

    if first_word.endswith("Пънче") or first_word.endswith("Месо") or first_word.endswith("Местообитание") :
        transformed_sentence = f"{first_word}то е {rest_of_sentence.lower()}"
    elif first_word.endswith("Шапка"):
        transformed_sentence = f"{first_word}та е {rest_of_sentence.lower()}"
    elif first_word.endswith("Сходни") and second_word.endswith("видове"):
        transformed_sentence = f"Относно сходните видове, {sentence[(len(first_word) + len(second_word) + 1):].strip().lower()}"
    elif (first_word.endswith("У") and second_word.endswith("нас")) or (first_word.endswith("По") and second_word.endswith("света")):
        transformed_sentence = f"{first_word} {second_word} я наричат {sentence[(len(first_word) + len(second_word) + 1):].strip()}"
    elif first_word.endswith("Коментар"):
        transformed_sentence = f"{rest_of_sentence.lower()}"
    elif first_word.endswith("Спори") or first_word.endswith("Ламели") or first_word.endswith("Пори"):
        transformed_sentence = f"{first_word}те са {rest_of_sentence.lower()}"
    if "(Източници" in transformed_sentence:
        transformed_sentence = re.sub(r"\s*\([^)]*\)", "", sentence).strip() 
        
    return transformed_sentence


def summarize_text(text, max_sentences=5):
    sentences = sent_tokenize(text)

    processed_sentences = [process_sentence(s) for s in sentences]

    # vectorize sentences with Count vectorizer, seems better than TF-IDF for the task (summary)
    # This step could be improved. BERT model?
    vectorizer = CountVectorizer()
    sentence_vectors = vectorizer.fit_transform(processed_sentences).toarray()

    # create a similarity matrix, then a graph
    similarity_matrix = cosine_similarity(sentence_vectors, sentence_vectors)
    nx_graph = nx.from_numpy_array(similarity_matrix)

    # calculate pagerank scores: how important is each sentence?
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(processed_sentences)), reverse=True)

    # Get top sentences as the summary
    summary = " ".join([s for _, s in ranked_sentences[:max_sentences]])
    return summary