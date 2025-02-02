from preprocess import preprocess_mushroom
# from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import json

class MushroomBot:
  exit_commands = ("стоп", "спри", "стига", "чао", "довиждане", "край")

  def __init__(self):
    # self.model = SentenceTransformer('sentence-transformers/LaBSE')
    with open("corpus/questions.json", "r", encoding="utf-8") as file:
      self.questions = json.load(file)

    with open("corpus/parsed_mushrooms_data.json", "r", encoding="utf-8") as file:
      self.mushrooms = json.load(file)

    with open("corpus/preprocessed_mushrooms.json", "r", encoding="utf-8") as file:
      self.preprocessed_mushrooms = json.load(file)

    self.vectorizers = {}
    self.tf_idf_vectors = {}
    for key in self.questions:
      docs = self.get_mushroom_values(self.preprocessed_mushrooms, key)
      self.vectorizers[key] = TfidfVectorizer()
      self.tf_idf_vectors[key] = self.vectorizers[key].fit_transform(docs)
    
    # self.mushrooms_embeddings = [self.model.encode(list(mushroom.values())) for mushroom in self.mushrooms]

  def welcome(self):
    print("Здравей, аз съм твоят помощник за разпознаване на гъби. 🍄 Ще ти задам няколко въпроса за гъбата, която искаш да идентифицираш и ще се постарая да намеря най-близкото съвпадение. Нека да започваме!")
  
  def chat(self):
    should_exit, input_mushroom = self.build_mushroom()
    if should_exit:
      return
    
    preprocessed_mushroom = preprocess_mushroom(input_mushroom)
    similarities = self.compute_similarities(preprocessed_mushroom)
    max_similarity_index = np.argmax(similarities)

    print(f"Best match: {self.mushrooms[max_similarity_index]['bgName']}")
    print(f"Similarity: {np.max(similarities)}")

    if "да" in input("Искаш ли да разпознаеш друга гъба? 🍄").lower():
      self.chat()

  def build_mushroom(self):
    mushroom = {key: "Няма информация" for key in self.questions}

    for key, questions in self.questions.items():
      for question in questions:
        reply = input(question + "\n")
        if self.should_exit(reply):
          return True, mushroom
        
        if self.is_unknown(reply):
          break
        
        mushroom[key] = reply if mushroom[key] == "Няма информация" else mushroom[key] + " " + reply
    
    return False, mushroom
  
  def is_unknown(self, reply):
    #TODO
    pass

  def should_exit(self, reply):
    for exit_command in self.exit_commands:
      if exit_command in reply.lower():
        return True
      
    return False

  def compute_similarities(self, mushroom):
    mushroom_tf_idf_vectors = {}
    for key in self.questions:
      docs = self.get_mushroom_values([mushroom], key)
      mushroom_tf_idf_vectors[key] = self.vectorizers[key].transform(docs)

    similarities = []
    for i in range(0, len(self.preprocessed_mushrooms)):
      similarities.append(self.compute_similarity(mushroom_tf_idf_vectors, i))

    return similarities
  
  def compute_similarity(self, mushroom_tf_idf_vectors, doc_index):
    key_similarities = {}

    for key in self.questions:
      similarity = cosine_similarity(mushroom_tf_idf_vectors[key][0], self.tf_idf_vectors[key][doc_index])
      key_similarities[key] = similarity

    return np.mean(list(key_similarities.values()))
  
  def get_mushroom_values(self, mushrooms, key):
    return [mushroom[key] for mushroom in mushrooms]
  
  # def compute_similarities(self, mushroom):
  #   input_mushroom_embeddings = self.model.encode(list(mushroom.values()))

  #   similarities = []
  #   for mushroom_embeddings in self.mushrooms_embeddings:
  #     similarities.append(self.compute_similarity(input_mushroom_embeddings, mushroom_embeddings))

  #   return similarities
  
  # def compute_similarity(self, input_mushroom_embeddings, mushroom_embeddings):
  #   semantic_similarities = []

  #   for i in range(0, len(self.questions)):
  #       similarity_attr = cosine_similarity([input_mushroom_embeddings[i]], [mushroom_embeddings[i]])[0][0]
  #       semantic_similarities.append(similarity_attr)

  #   return np.mean(semantic_similarities)

  def goodbye(self):
    print("Беше ми приятно да ти помагам с разпознаването на гъби! 🍄 Ако имаш още въпроси или срещнеш нови гъби, не се колебай да ме потърсиш отново. До скоро! 👋")

mushroom_bot = MushroomBot()

mushroom_bot.welcome()
mushroom_bot.chat()
mushroom_bot.goodbye()
