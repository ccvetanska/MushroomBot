from preprocess import preprocess_mushroom
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from rich.console import Console
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import json

class MushroomBot:
  exit_commands = ("стоп", "спри", "стига", "чао", "довиждане", "край")
  underside_values = {"gills": ("ламели", "ресни"), "pores": ("пори"), "tubes": ("тръбички", "дълбоки пори")}
  console = Console()

  GREEN = "\033[38;5;77m"
  RED = "\033[38;5;196m"
  RESET = "\033[0m"

  def __init__(self):
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

  def welcome(self):
    print(self.format_message("Здравей, аз съм твоят помощник за разпознаване на гъби. 🍄 Ще ти задам няколко въпроса за гъбата, която искаш да идентифицираш и ще се постарая да намеря най-близкото съвпадение. Нека да започваме!"))
  
  def chat(self):
    should_exit, input_mushroom = self.build_mushroom()
    if should_exit:
      return
    
    preprocessed_mushroom = preprocess_mushroom(input_mushroom)
    similarities = self.compute_similarities(preprocessed_mushroom)

    self.print_response(similarities)

    if "да" in input(self.format_message("Искаш ли да разпознаеш друга гъба? 🍄")).lower():
      self.chat()

  def build_mushroom(self):
    mushroom = {key: "Няма информация" for key in self.questions}

    for key, questions in self.questions.items():
      if key in self.underside_values and mushroom["underside"].lower() not in self.underside_values[key]:
        continue

      for question in questions:
        reply = input(self.format_message(question))
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

  def print_response(self, similarities):
    sorted_indices = np.argsort(similarities)[::-1]
    best_match = self.mushrooms[sorted_indices[0]]

    response = f"Благодаря за описанието! Въз основа на твоите отговори, най-вероятната гъба ({similarities[sorted_indices[0]]}%) е {best_match['bgName']} ({best_match['latinTitle']})"

    response += f" ({best_match['images'][0]})\n\n" if best_match['images'] and best_match['images'][0] else ".\n\n"

    response += f"{best_match['summary']}\n\n"
      
    second_best_match = self.mushrooms[sorted_indices[1]]
    if(second_best_match):
      response += f"Втората най-вероятна гъба ({similarities[sorted_indices[1]]}%) е {second_best_match['bgName']} ({second_best_match['latinTitle']})."
      
      third_best_match = self.mushrooms[sorted_indices[2]]
      if(third_best_match):
        response += f" Третата по вероятност ({similarities[sorted_indices[2]]}%) е {third_best_match['bgName']} ({third_best_match['latinTitle']})."
    
    print(self.format_message(response))

    print(self.format_important_message("ВНИМАНИЕ: Никога не яжте гъби само въз основа на информация в интернет и/или препоръките на този бот! Консумацията на отровни видове може да доведе до необратими последствия и смърт, а идентифицирането им е сложен процес, изискващ много опит."))

  def goodbye(self):
    print(self.format_message("Беше ми приятно да ти помагам с разпознаването на гъби! 🍄 Ако имаш още въпроси или срещнеш нови гъби, не се колебай да ме потърсиш отново. До скоро! 👋"))
  
  def format_message(self, message):
    return f"\n{self.GREEN}{message}{self.RESET}\n"
  
  def format_important_message(self, message):
    return f"\n{self.RED}{message}{self.RESET}\n"

mushroom_bot = MushroomBot()

mushroom_bot.welcome()
mushroom_bot.chat()
mushroom_bot.goodbye()
