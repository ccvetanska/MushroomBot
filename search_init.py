import json
from elasticsearch import Elasticsearch

with open("corpus/parsed_mushrooms_data.json", "r", encoding="utf-8") as file:
    mushrooms = json.load(file)

with open("config/elastic_credentials.json", "r") as file:
    credentials = json.load(file)

username = credentials["username"]
password = credentials["password"]

if not username or not password:
    raise Exception("Elasticsearch credentials are missing")

es = Elasticsearch(f"http://{username}:{password}@localhost:9200")

index_name = "mushrooms"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body={
        "mappings": {
            "properties": {
                "habitat": {"type": "text"},
                "cap": {"type": "text"},
                "body": {"type": "text"},
                "stem": {"type": "text"},
                "flesh": {"type": "text"},
                "gills": {"type": "text"},
                "tubes": {"type": "text"},
                "pores": {"type": "text"},
                "underside": {"type": "keyword"},
                "ring": {"type": "text"},
                "spores": {"type": "text"},
            }
        }
    })

for i, mushroom in enumerate(mushrooms):
    es.index(index=index_name, id=i+1, body=mushroom)

def search_mushrooms(user_answers):
    query = {
        "query": {
            "bool": {
                "should": [],
                "minimum_should_match": 1  # to find at lest one match
            }
        }
    }

    for field, value in user_answers.items():
        query["query"]["bool"]["should"].append({
            "match": {
                field: {
                    "query": value,
                    "fuzziness": "AUTO"  # allow errors and typos in the search query(answers)
                }
            }
        })

    response = es.search(index=index_name, body=query)

    # return the best matched 3 mushrooms
    if response["hits"]["hits"]:
        return response["hits"]["hits"][0]["_source"], response["hits"]["hits"][1]["_source"], response["hits"]["hits"][2]["_source"], 
    else:
        return None