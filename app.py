import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# ----------------------------
# Title
# ----------------------------
st.title("📈 Nifty 50: Buy/Sell Signal Detector (Last 1 Month)")

# ----------------------------
# Fetch Nifty50 Stocks (Fallback)
# ----------------------------
@st.cache_data
def get_nifty50_symbols():
    try:
        import requests
        url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        df = pd.read_csv(pd.compat.StringIO(response.text))
        return list(df["Symbol"].str.strip() + ".NS")
    except:
        st.warning("⚠️ Could not fetch live Nifty 50 list. Using fallback list.")
        return [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "KOTAKBANK.NS", "HINDUNILVR.NS", "LT.NS", "SBIN.NS", "ITC.NS"
        ]

# ----------------------------
# Fetch stock data
# ----------------------------
@st.cache_data
def get_stock_data(ticker):
    end = datetime.now()
    start = end - timedelta(days=30)
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        return None
    df["MA7"] = df["Close"].rolling(window=7).mean()
    df["MA21"] = df["Close"].rolling(window=21).mean()
    return df

# ----------------------------
# Generate Buy/Sell signals
# ----------------------------
def generate_signals(df):
    df["Signal"] = ""
    for i in range(1, len(df)):
        if df["MA7"][i] > df["MA21"][i] and df["MA7"][i - 1] <= df["MA21"][i - 1]:
            df.at[df.index[i], "Signal"] = "Buy"
        elif df["MA7"][i] < df["MA21"][i] and df["MA7"][i - 1] >= df["MA21"][i - 1]:
            df.at[df.index[i], "Signal"] = "Sell"
    return df

# ----------------------------
# Main logic
# -------
