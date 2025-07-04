# morocco-tourism-analytics

# 🧭 Tourism Analysis in Morocco via Reddit

## 📌 Project Objective

This project aims to **extract, clean, and analyze Reddit discussions** related to **tourism in Morocco**, with the goal of understanding:

- The most frequently mentioned destinations
- Visitor sentiments (positive, negative, neutral)
- Thematic trends (accommodation, culture, food, etc.)

---

## ⚙️ Tech Stack

| Component         | Tools Used                            |
|------------------|----------------------------------------|
| **Reddit Scraping**     | [`PRAW`](https://praw.readthedocs.io/en/latest/) (Reddit API) |
| **Storage**             | MongoDB                             |
| **Cleaning & NLP**      | `pandas`, `TextBlob`                |
| **Visualization**       | `Streamlit`, `Seaborn`, `Folium`   |

---

## 1️⃣ Step 1 – Scraping Reddit

- Automated query generation:  
  *"travel to Marrakech"*, *"is Fes safe for tourists"*, etc.
- Collection of **both posts and comments**
- Storage in **MongoDB** with unique `_id` to avoid duplicates
- Around **50 cities and villages** analyzed using 10 query templates each

---

## 2️⃣ Step 2 – Data Cleaning

Structured cleaning pipeline:
- Remove duplicates
- Merge `title` + `text` into `content`
- Spam filtering (e.g., `.com`, `buy now`, `http`, short texts)
- Validate tourism relevance via keyword matching
- Final filtering: content must include **at least 2 tourism-related keywords**

### 📊 Cleaning Results:

| Step                      | Remaining Rows |
|---------------------------|----------------|
| Raw Dataset               | 121,866        |
| After spam filtering      | 38,497         |
| After tourism validation  | 18,562         |

---

## 3️⃣ Step 3 – Data Enrichment

- **Sentiment analysis** using `TextBlob` → `Positive`, `Neutral`, `Negative`
- **Multi-label thematic classification** (e.g., Accommodation, Security, Nature, etc.)
- **City type** (City or Village)
- **Geo-coordinates** added via external CSV

---

## 4️⃣ Step 4 – Interactive Visualization with Streamlit

A user-friendly dashboard built with **Streamlit** to explore the cleaned dataset.

### ✨ Features:

- Dynamic filters:
  - Location type (City/Village)
  - Specific cities
  - Sentiment category
  - Tourism themes
- Visualizations:
  - Top 10 most discussed cities
  - Theme distribution
  - Sentiment distribution
  - Top keywords per theme
- **Folium map** showing city mentions
- Text preview of Reddit posts/comments

### ▶️ Run the dashboard:

```bash
streamlit run app_dashboard.py
