import yfinance as yf
import pandas as pd

def load_price_data(symbol='ETH-USD', period='30d'):
    try:
        df = yf.download(symbol, period=period, interval='1d')
        df.reset_index(inplace=True)
        df = df.rename(columns={"Date": "date", "Close": "close"})
        return df
    except Exception as e:
        print(f"Failed to load price data: {e}")
        return None
