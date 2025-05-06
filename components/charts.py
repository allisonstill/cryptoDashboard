import streamlit as st
import pandas as pd
import altair as alt

def plot_price_chart(df):
    chart = alt.Chart(df).mark_line().encode(
        x='date:T',
        y='close:Q',
        tooltip=['date:T', 'close:Q']
    ).properties(
        width='container',
        height=300
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def plot_sentiment_score(df):
    avg_score = df['score'].mean()
    st.metric("Average Sentiment Score", f"{avg_score:.2f}")

def plot_sentiment_over_time(df):
    df = df.copy()
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["day"] = pd.to_datetime(df["published_at"]).dt.floor('D')
    grouped = df.groupby("day")["score"].mean().reset_index(name="avg_score")

    # Optional: add 7-day rolling average
    grouped["rolling_avg"] = grouped["avg_score"].rolling(window=7, min_periods=1).mean()

    base = alt.Chart(grouped).encode(x='day:T')

    bars = base.mark_bar(color="steelblue").encode(
        y=alt.Y('avg_score:Q', title="Average Sentiment Score"),
        tooltip=['day:T', 'avg_score:Q']
    )

    line = base.mark_line(color="orange").encode(
        y=alt.Y('rolling_avg:Q', title="7-Day Rolling Avg"),
        tooltip=['day:T', 'rolling_avg:Q']
    )

    chart = (bars + line).properties(height=300, width='container')
    st.altair_chart(chart, use_container_width=True)
