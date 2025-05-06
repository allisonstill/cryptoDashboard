import requests
import pandas as pd
from data.newsdata import fetch_newsdata_sentiment
import os
from dotenv import load_dotenv

load_dotenv()

CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
MAX_PAGES = 3
sentiment_mapping = {"positive": 1, "neutral": 0, "negative": -1}

sentiment_mapping = {"positive": 1, "neutral": 0, "negative": -1}

def load_sentiment_data(currency="ETH", api_key=CRYPTOPANIC_API_KEY, pages=MAX_PAGES):
    all_rows = []

    try:
        for page in range(1, pages + 1):
            url = (
                f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}"
                f"&currencies={currency}&public=true&kind=news&page={page}"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            articles = data.get("results", [])

            for article in articles:
                sentiment_tag = article.get("sentiment", None)
                votes = article.get("votes", {})
                vote_score = votes.get("positive", 0) - votes.get("negative", 0)

                if sentiment_tag in sentiment_mapping:
                    sentiment_score = sentiment_mapping[sentiment_tag]
                    sentiment = sentiment_tag
                else:
                    sentiment_score = vote_score
                    sentiment = "vote-based"

                all_rows.append({
                    "title": article.get("title"),
                    "published_at": article.get("published_at"),
                    "sentiment": sentiment,
                    "score": sentiment_score,
                    "source": article.get("domain"),
                    "url": article.get("url")
                })

        crypto_df = pd.DataFrame(all_rows)
        coin_name = {
            "ETH": "ethereum",
            "BTC": "bitcoin",
            "SOL": "solana"
        }.get(currency, "ethereum")

        newsdata_df = fetch_newsdata_sentiment(coin_name)

        if not newsdata_df.empty:
            combined_df = pd.concat([crypto_df, newsdata_df], ignore_index=True)
        else:
            combined_df = crypto_df

        return combined_df
    except Exception as e:
        print(f"Failed to load sentiment data: {e}")
        return None
