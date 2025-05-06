import streamlit as st
from data.prices import load_price_data
from data.news import load_sentiment_data
from components.charts import plot_price_chart, plot_sentiment_score, plot_sentiment_over_time
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(page_title="Crypto Intelligence Dashboard", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #2e3b4e;
    }
    .stTabs [role="tab"] {
        background: #e4e8f0;
        padding: 10px 20px;
        border-radius: 6px;
        margin-right: 6px;
        font-weight: 600;
        color: #2e3b4e;
    }
    .stTabs [aria-selected="true"] {
        background: #2962ff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

COINS = {
    "Ethereum (ETH)": {"symbol": "ETH-USD", "panic": "ETH"},
    "Bitcoin (BTC)": {"symbol": "BTC-USD", "panic": "BTC"},
    "Solana (SOL)": {"symbol": "SOL-USD", "panic": "SOL"}
}

st.sidebar.title("Dashboard Settings")
coin_choice = st.sidebar.selectbox("Select Cryptocurrency", list(COINS.keys()))
selected = COINS[coin_choice]

st.markdown("""
<div style='display: flex; align-items: center; gap: 20px;'>
    <h1 style='margin: 0;'>CryptoIntel Dashboard</h1>
</div>
<hr style='margin-top: 0; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Market", "News Sentiment", "Insights"])

with tab1:
    st.subheader(f"{coin_choice} Price - Last 30 Days")
    df_price = load_price_data(selected['symbol'])
    if df_price is not None:
        plot_price_chart(df_price)

with tab2:
    st.subheader(f"{coin_choice} News Sentiment (via CryptoPanic + NewsData.io)")
    sentiment_df = load_sentiment_data(selected['panic'])
    if sentiment_df is not None:
        plot_sentiment_score(sentiment_df)

        for _, row in sentiment_df.iterrows():
            with st.expander(f"{row['title'][:100]}..."):
                st.write(f"**Sentiment**: {row['sentiment'].capitalize()} ({row['score']:.2f})")
                if pd.notna(row.get("published_at")):
                    st.write(f"**Published**: {row['published_at']}")
                if pd.notna(row.get("url")):
                    st.markdown(f"[Read more]({row['url']})")

with tab3:
    st.subheader("Sentiment Over Time")
    if sentiment_df is not None:
        sentiment_df = sentiment_df.copy()
        sentiment_df["published_at"] = pd.to_datetime(sentiment_df["published_at"], errors="coerce")
        sentiment_df = sentiment_df.dropna(subset=["published_at"])
        sentiment_df["day"] = sentiment_df["published_at"].dt.floor('D')

        plot_sentiment_over_time(sentiment_df)

        st.subheader("Frequent Terms in Headlines")
        text = " ".join(sentiment_df["title"].dropna().tolist())
        wordcloud = WordCloud(width=800, height=300, background_color='white').generate(text)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        st.subheader("Sentiment Score Distribution")
        hist = alt.Chart(sentiment_df).mark_bar().encode(
            alt.X("score:Q", bin=alt.Bin(maxbins=20), title="Sentiment Score"),
            y='count()',
            tooltip=['count()']
        ).properties(width='container', height=300)
        st.altair_chart(hist, use_container_width=True)