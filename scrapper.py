import requests
import csv
from bs4 import BeautifulSoup
import pandas as pd
import time, random

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



# now merge all lines with equal "Latin-Title"
def buildGroupedMushroomsCsv(filename):
    df = pd.read_csv('mushrooms.csv')
    df_grouped = df.groupby('Latin-Title').agg({
        'Bulgarian-Title': lambda x: '|'.join(map(str, x)), 
        **{col: 'first' for col in df.columns if col != 'Latin-Title' and col != 'Bulgarian-Title'} 
    }).reset_index()
    df_grouped.to_csv(filename, sep='\t', index=False)
    return df_grouped



buildAllMushroomsCsv("mushrooms.csv")
df_grouped = buildGroupedMushroomsCsv('mushrooms-grouped.csv')

df_full_info = pd.read_csv("mushrooms-full-info.csv", sep='\t')

for index, row in df_grouped.iterrows():
    time.sleep(random.randint(2,4)) # avoid getting blocked
    dict = row.to_dict()
    fullInfoUrl = dict['Resource-URL']
    response = requests.get(fullInfoUrl)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        pageBody = soup.find(class_= "post-bodycopy")
        characteristics = pageBody.find_all("strong")
        images = pageBody.find_all("img")
        new_df = pd.DataFrame({'Latin-Title': [dict['Latin-Title']], 'Bulgarian-Title': [dict['Bulgarian-Title']],'Resource-URL': [dict['Resource-URL']]})
        for c in characteristics:
            cName = c.get_text(strip=True)
            cContent = ""
            for sibling in c.next_siblings:
                if sibling.name == 'strong':
                    break
                cContent += sibling.get_text(strip=True) if hasattr(sibling, 'get_text') else str(sibling).strip()
                cContent += " "
            if cName and cContent:
                new_df[cName] = cContent
        for i, img in enumerate(images):
            new_df[f"Image-{i+1}"] = img['src']
        df_full_info = pd.concat([df_full_info, new_df], ignore_index=True)
        df_full_info.to_csv("mushrooms-full-info.csv", sep='\t', index=False)
    else:            
        print(f"Request to {fullInfoUrl} failed. Code: {response.status_code}")
                         
    # ensure we do not make too many requests when testing
    #if(index == 5): break


#df_full_info.to_csv("mushrooms-full-info.csv", sep='\t', index=False)