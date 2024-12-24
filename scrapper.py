import requests
import csv
from bs4 import BeautifulSoup
import pandas as pd

def buildAllMushroomsCsv(filename):
    url = "https://manatarka.org/list-bg/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all("em")  
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:        
            writer = csv.writer(file)
            writer.writerow(["Latin-Title", "Bulgarian-Title", "Resource-URL"])
            for i, em in enumerate(all_links):
                latin_title = em.string
                if(em.previous_sibling):
                    try:          
                        bg_title = em.previous_sibling.split(" (")[0]
                        link = em.contents[0].attrs["href"]    
                        writer.writerow([latin_title.strip(), bg_title.strip(), link.strip()])
                    except AttributeError:
                        print(f"{bg_title} has no associated url")

    else:
        print(f"Request to {url} failed. Code: {response.status_code}")


buildAllMushroomsCsv("mushrooms.csv")

# now merge all lines with equal "Latin-Title"
df = pd.read_csv('mushrooms.csv')
df_grouped = df.groupby('Latin-Title').agg({
    'Bulgarian-Title': lambda x: '|'.join(map(str, x)), 
    **{col: 'first' for col in df.columns if col != 'Latin-Title' and col != 'Bulgarian-Title'} 
}).reset_index()
df_grouped.to_csv('mushrooms-grouped.csv', index=False)