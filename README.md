# 🧭 Morocco Tourism Analytics via Reddit

## 📌 Overview

This project **extracts, cleans, and analyzes Reddit discussions about Moroccan tourism** to:

* Identify frequently discussed destinations
* Analyze visitor sentiments (positive, neutral, negative)
* Discover thematic trends (accommodation, safety, food, etc.)

---

## ⚙️ Tech Stack

* **Scraping:** PRAW (Reddit API)
* **Storage:** MongoDB
* **Cleaning & NLP:** pandas, TextBlob
* **Visualization:** Streamlit, Seaborn, Folium

---

## 🚀 Pipeline

### 1️⃣ Scraping Reddit

* Automated queries ("travel to Marrakech", "is Fes safe", etc.)
* Collect posts and comments for \~50 cities and villages
* Store data in MongoDB with deduplication

### 2️⃣ Data Cleaning

* Remove duplicates and merge `title` + `text`
* Spam filtering (URLs, promotions, short posts)
* Filter for tourism relevance (2+ tourism-related keywords)

**Cleaning Progress:**

| Step                      | Rows Remaining |
| ------------------------- | -------------- |
| Raw scraped data          | 121,866        |
| After spam filtering      | 38,497         |
| After relevance filtering | 18,562         |

### 3️⃣ Data Enrichment

* Sentiment analysis using TextBlob
* Thematic classification (Accommodation, Security, etc.)
* Geolocation and place type tagging

### 4️⃣ Visualization with Streamlit

* Dynamic filters: city, sentiment, theme, place type
* Visualizations: top cities, theme & sentiment distribution, keyword trends
* Folium map with mentions by city
* Preview Reddit post excerpts

---

## 🗂️ Dataset Download

The dataset is too large for GitHub.

1️⃣ Download the cleaned dataset from [Kaggle](https://www.kaggle.com/datasets/aymannaaimi/datset-for-moroccan-tourism-analytics/data).
2️⃣ Create a folder named `Data` in the project root.
3️⃣ Place `maroc_villes.csv` inside `DATA`.

---

## ▶️ Run Locally

**Launch the dashboard:**

```bash
streamlit run app_dashboard.py
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

---

## 🎯 Why This Project Matters

This project demonstrates how **social media data can enrich tourism analysis in Morocco**, supporting:

* Regional tourism boards
* Researchers analyzing travel perceptions
* Data-driven tourism strategies

---

## 📄 License

MIT License.

---

## 🙌 Author

**Ayman Naaimi**
Master's in Data Science for Smart Manufacturing, ENSAM Meknès.

[GitHub Repository](https://github.com/6ym6n/morocco-tourism-analytics)
