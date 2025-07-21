import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from niftystocks import nifty500

st.title("🇮🇳 Nifty 500 Trading Signal Scanner")

# Fetch Indian tickers with .NS
tickers = [sym + ".NS" for sym in nifty500.get_symbols()]

# Limit scan count to avoid rate limits
MAX_TICKERS = st.sidebar.slider("Max tickers to scan", 50, 500, 200)
tickers = tickers[:MAX_TICKERS]

results = []

for ticker in tickers:
    data = yf.download(ticker, period="200d", interval="1d", progress=False)
    if data.empty or set(["Close", "High", "Volume"]) - set(data.columns):
        continue
    if len(data) < 130:
        continue

    data['High_125'] = data['High'].rolling(125).max()
    data['SMA_Vol_125'] = data['Volume'].rolling(125).mean()
    data['RSI_14'] = ta.momentum.RSIIndicator(
        close=data['Close'].fillna(method='ffill'), window=14
    ).rsi()
    data['High_125_1d'] = data['High_125'].shift(1)
    data['SMA_Vol_1d'] = data['SMA_Vol_125'].shift(1)
    data.dropna(inplace=True)

    latest = data.iloc[-1]
    prev = data.iloc[-2]
    if (
        latest['Close'] > max(prev['High_125_1d'], latest['High'])
        and latest['Volume'] > 2 * prev['SMA_Vol_1d']
        and latest['RSI_14'] < 70
    ):
        results.append({
            "Ticker": ticker,
            "Close": latest['Close'],
            "Volume": latest['Volume'],
            "RSI_14": round(latest['RSI_14'], 2)
        })

# Display results
if results:
    df = pd.DataFrame(results)
    st.success(f"🎯 {len(df)} buy signals found!")
    st.dataframe(df)
else:
    st.info("No buy signals detected today.")

