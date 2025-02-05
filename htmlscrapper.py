import pandas as pd
import os
import requests
import time
import random
import json
from bs4 import BeautifulSoup
from summarizer import summarize_text


def downloadHtmlPages():
    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Open the CSV file
    with open('mushrooms-grouped.csv', newline='', encoding='utf-8' ) as csvfile:
        df_grouped = pd.read_csv("mushrooms-grouped.csv", sep='\t')
        
        # Iterate through each row in the CSV
        for index, row in df_grouped.iterrows():
            time.sleep(random.randint(2,4)) # avoid getting blocked
            dict = row.to_dict()
            resource_url = dict['Resource-URL']
            latin_title = dict['Latin-Title']
            
            # Make a request to the resource URL
            response = requests.get(resource_url)
            
            # Save the content to an HTML file
            file_path = os.path.join('data', f"{latin_title}.html")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text) 


HTML_FOLDER = "data/"


def parse_mushroom_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    bg_title = soup.find("h2").text.strip() if soup.find("h2") else "Неизвестно"
    latin_title = file_path.split("/")[-1].replace(".html", "")

    # put here all the information about this mushroom, 
    # there could be some paragraphs that don't have a <strong> tag as title
    # and therefore are not extracted in the loop below
    description_div = soup.find("div", class_="post-bodycopy")
    
    if not description_div: # probably a 404 page
        return None

    description = " ".join([p.get_text() for p in description_div.find_all("p") if "wp-caption-text" not in p.get('class', [])]) if description_div else ""

    description_summary = summarize_text(description)

    bg_alias = "Няма информация"
    world_alias = "Няма информация"
    body = "Няма информация"
    cap = "Няма информация"
    stem = "Няма информация"
    flesh = "Няма информация"
    habitat = "Няма информация"
    edibility = "Няма информация"
    ring = "Няма информация"
    spores = "Няма информация"
    gills = "Няма информация"
    tubes = "Няма информация"
    pores = "Няма информация"
    underside = "Няма информация"
    similar_species = "Няма информация"

    for p in soup.find_all("p"):
        strong_text = p.find("strong")
        if strong_text:
            if "Световни синоними" in strong_text.text:
                world_alias = p.text.replace(strong_text.text, "").strip()
            if ("Плодно тяло" in strong_text.text) or ("тяло" in strong_text.text):
                body = p.text.replace(strong_text.text, "").strip()
            if "Шапка" in strong_text.text:
                cap = p.text.replace(strong_text.text, "").strip()
            if ("Пънче" in strong_text.text) or ("пън" in strong_text.text):
                stem = p.text.replace(strong_text.text, "").strip()
            if "Месо" in strong_text.text:
                flesh = p.text.replace(strong_text.text, "").strip()
            if "Местообитание" in strong_text.text:
                habitat = p.text.replace(strong_text.text, "").strip()
            if "У нас" in strong_text.text:
                bg_alias = p.text.replace(strong_text.text, "").strip()
            if "По света" in strong_text.text:
                world_alias = p.text.replace(strong_text.text, "").strip()
            if ("Ядливост" in strong_text.text) or ("Коментар" in strong_text.text):
                edibility = p.text.replace(strong_text.text, "").strip()
            if "Пръстен" in strong_text.text:
                ring = p.text.replace(strong_text.text, "").strip()
            if "Спори" in strong_text.text:
                spores = p.text.replace(strong_text.text, "").strip()
            if "Ламели" in strong_text.text:    
                gills = p.text.replace(strong_text.text, "").strip()
                underside = "Ламели"
            if "Тръбички" in strong_text.text:    
                tubes = p.text.replace(strong_text.text, "").strip()
                underside = "Тръбички"
            if "Пори" in strong_text.text:    
                pores = p.text.replace(strong_text.text, "").strip()
                underside = "Пори"
            if "Сходни видове" in strong_text.text:   
                similar_species = p.text.replace(strong_text.text, "").strip()
        


    # find toxins if any
    toxins = "Няма информация"
    for p in soup.find_all("p"):
        if ("токсин" in p.text) or ("киселин" in p.text):
            toxins = p.text.strip()

    # Extract images
    images = []
    for img in soup.find_all("img"):
        img_src = img.get("src")
        if img_src and img_src.endswith((".jpg", ".png", ".jpeg")) and "sitepress-multilingual-cms" not in img_src:
            images.append(img_src)

    return {
        "latinTitle": latin_title,
        "bgName": bg_title,
        "bgAlias": bg_alias,
        "worldAlias": world_alias,
        "edibility": edibility,
        "cap": cap,
        "body": body,
        "stem": stem,
        "flesh": flesh,
        "gills": gills,
        "tubes": tubes,
        "pores": pores,
        "underside": underside,
        "ring": ring,
        "spores": spores,
        "habitat": habitat,
        "toxins": toxins,
        "similarSpecies": similar_species,
        "images": images,
        "fullDescription": description,
        "summary": description_summary
    }

# Download HTML pages
# downloadHtmlPages()

# Read all HTML files and extract data
mushroom_data = []
for filename in os.listdir(HTML_FOLDER):
    if filename.endswith(".html"):
        file_path = os.path.join(HTML_FOLDER, filename)
        data = parse_mushroom_html(file_path)
        if data:
             mushroom_data.append(data)

# Save the data to a JSON file
output_file = os.path.join("corpus/", "parsed_mushrooms_data.json")
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(mushroom_data, json_file, ensure_ascii=False, indent=4)

print(f"✅ Извлечени данни за {len(mushroom_data)} гъби! Запазени в {output_file}")
