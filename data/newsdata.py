import requests
import pandas as pd
from transformers import pipeline
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
BASE_URL = "https://newsdata.io/api/1/news"
sentiment_pipeline = pipeline("sentiment-analysis")

@st.cache_data(ttl=3600)
def fetch_newsdata_sentiment(coin_name="ethereum", limit=15):
    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": coin_name,
        "language": "en"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" not in data or not data["results"]:
            st.warning("⚠️ NewsData returned no results.")
            return pd.DataFrame([])

        articles = data["results"][:limit]
        rows = []

        for article in articles:
            title = article.get("title")
            url = article.get("link")
            pubdate = article.get("pubDate")

            if not title:
                continue

            sentiment = sentiment_pipeline(title)[0]
            score = sentiment['score'] * (-1 if sentiment['label'] == 'NEGATIVE' else 1)

            rows.append({
                "title": title,
                "sentiment": sentiment['label'].lower(),
                "score": score,
                "url": url,
                "published_at": pubdate,
                "source": "NewsData.io"
            })

        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"NewsData fetch failed: {e}\nURL: {response.url if 'response' in locals() else BASE_URL}")
        return pd.DataFrame([])
