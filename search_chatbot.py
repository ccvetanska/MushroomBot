from search_init import search_mushrooms
import json

def ask_questions():
    with open("corpus/questions.json", "r", encoding="utf-8") as file:
      questions = json.load(file)


    user_answers = {}
    for key in questions:
        user_answers[key] = ""
        if(questions[key] == None):
            continue
        for question in questions[key]:
            user_answers[key] += " "+ input(f"\n{question}\n ").strip().lower()

        if key == "underside": 
            undersideValue = user_answers[key].strip().lower()
            if undersideValue == "ламели":
                questions["tubes"] = None
                questions["pores"] = None
            if(undersideValue == "пори"):
                questions["gills"] = None
                questions["tubes"] = None
            if(undersideValue == "тръбички"):
                questions["gills"] = None
                questions["pores"] = None
    return user_answers

# Start the chatbot
user_inputs = ask_questions()
result = search_mushrooms(user_inputs)
best_match = result[0]
second_match = result[1]
third_match = result[2]

if best_match:
    print(f"\nБлагодаря за описанието! Въз основа на твоите отговори, най-вероятната гъба е {best_match["bgName"]}, ({best_match["latinTitle"]}).")
    print("Снимка: ", best_match["images"][0])
    print(best_match["summary"])
    if second_match:
        print("\nДруги възможности са:")
        print(f"{second_match["bgName"]} ({second_match["latinTitle"]}), снимка: {second_match["images"][0]}")
        if(third_match):
            print(f"{third_match["bgName"]} ({third_match["latinTitle"]}), снимка: {third_match["images"][0]}")
else:
    print("\nНе успях да намеря точнo съвпадение.")

