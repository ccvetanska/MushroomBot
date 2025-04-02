# 🍄 Bulgarian Mushroom Identification Assistant

A text-based system for identifying wild mushrooms in Bulgaria based on user-provided descriptions.

## 📌 Overview

This project aims to support amateur mycologists by providing a system that identifies mushrooms based on descriptive input rather than images. The system is tailored specifically to mushrooms found in Bulgaria and consists of two main components:
- A **chatbot**, which asks users about the characteristics of a mushroom and predicts the closest match.
- A **search engine**, which uses the same inputs to return the closest mushroom from a structured dataset.

---

## 🧠 Design

We divided the task into the following key components:

1. **Data Extraction**  
   We contacted the creators of [www.manatarka.org](http://www.manatarka.org) and, with permission, used the site as our primary data source.

2. **Chatbot Implementation**  
   A system that asks the user questions about mushroom characteristics and returns the most similar species from our dataset.

3. **Search Engine Implementation**  
   An alternative approach using the same questions as input queries for a local Elasticsearch instance, returning the most relevant result.

---

## ⚙️ Technologies Used

- **Python**
- **BeautifulSoup** – Web scraping
- **pandas** – CSV file handling
- **nltk**, **Stanza** – Text preprocessing (tokenization, lemmatization, POS-tagging in Bulgarian)
- **scikit-learn** – TF-IDF vectorization
- **Elasticsearch** – Search engine setup
- **networkx** – Summarization

---

## 🕸️ Web Scraping

We scraped 489 individual mushroom entries from manatarka.org by:
- Extracting an index of mushroom names with links
- Normalizing and grouping by name to eliminate duplicates
- Saving the data as `.csv` and HTML files
- Parsing and structuring each mushroom page into a JSON object with fields like:

```json
{
  "latinTitle": "Tricholoma aurantium",
  "bgName": "Оранжева есенна гъба",
  "cap": "...",
  "stem": "...",
  "habitat": "...",
  "spores": "...",
  ...
}
```

---

## 🤖 Chatbot

The chatbot processes user descriptions and compares them with preprocessed entries from the dataset:

- Text preprocessing includes tokenization, lemmatization, and POS-tagging.
- Each characteristic is vectorized using `TfidfVectorizer`.
- Cosine similarity is calculated between user input and each entry.
- The mushroom with the highest average similarity is returned.

---

## 🔍 Search Engine

- We set up a local **Elasticsearch** server with the following index structure:

```json
"mappings": {
  "properties": {
    "cap": {"type": "text"},
    "stem": {"type": "text"},
    "gills": {"type": "text"},
    ...
    "underside": {"type": "keyword"}
  }
}
```

- `"fuzziness": "AUTO"` is enabled for tolerant queries.
- User inputs are used directly as query parameters to return the closest match.

---

## 🧪 Experiments

We ran 10 manual tests with identical inputs for both the chatbot and search engine:

| Method         | Correct Matches | Accuracy |
|----------------|------------------|----------|
| Chatbot        | 6/10             | 60%      |
| Search Engine  | 8/10             | 80%      |

More extensive testing is required for reliable evaluation. (See Figures 1 and 2 in full report.)

---

## ✅ Conclusion

- We successfully built a structured mushroom dataset tailored to Bulgarian species.
- Both the chatbot and search engine approaches perform reasonably well given the dataset size.
- Future improvements may include:
  - **Semantic matching** using sentence embeddings (chatbot)
  - **Synonym dictionaries** and controlled vocabularies (search engine)

---

## 📂 Data Example

Check the `corpus/` folder for a sample structure of the extracted mushrooms. You can find the raw scrapped HTML in `data/`


