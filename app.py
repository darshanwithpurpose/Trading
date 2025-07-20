import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# 🔁 Cache static fallback list of Nifty 50 symbols
@st.cache_data
def get_nifty50_symbols():
    return [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "KOTAKBANK",
        "HINDUNILVR", "LT", "SBIN", "ITC", "BHARTIARTL", "AXISBANK",
        "BAJFINANCE", "HCLTECH", "WIPRO", "MARUTI", "NTPC", "TITAN",
        "SUNPHARMA", "POWERGRID", "NESTLEIND", "ULTRACEMCO", "TECHM",
        "JSWSTEEL", "TATAMOTORS", "ADANIENT", "COALINDIA", "ONGC",
        "GRASIM", "ADANIPORTS", "HDFCLIFE", "BRITANNIA", "CIPLA",
        "DIVISLAB", "BPCL", "HINDALCO", "HEROMOTOCO", "BAJAJ_AUTO",
        "SBILIFE", "DRREDDY", "BAJAJFINSV", "APOLLOHOSP", "INDUSINDBK",
        "ICICIPRULI", "TATACONSUM", "SHREECEM", "MM", "UPL"
    ]

# 📉 RSI Calculation
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = -delta.clip(upper=0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 📊 MACD Calculation
def calculate_macd(data):
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

# ✅ Strategy Logic
def generate_signals(df):
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['SignalLine'] = calculate_macd(df)
    df['Buy'] = (df['RSI'] < 30) & (df['MACD'] > df['SignalLine'])
    df['Sell'] = (df['RSI'] > 70) & (df['MACD'] < df['SignalLine'])
    return df.dropna()

# 🚀 Streamlit UI
st.title("📈 Nifty 50 AI Strategy: RSI + MACD Signals")
st.write("Buy: RSI < 30 and MACD > Signal | Sell: RSI > 70 and MACD < Signal")

symbols = get_nifty50_symbols()
selected = st.multiselect("Select Stocks", symbols, default=symbols[:5])

start_date = datetime.today() - timedelta(days=30)

for symbol in selected:
    st.subheader(f"🔍 {symbol}")
    try:
        df = yf.download(f"{symbol}.NS", start=start_date, progress=False)
        if df.empty or 'Close' not in df.columns:
            st.warning("⚠️ No valid data returned.")
            continue

        df = generate_signals(df)

        if 'Close' in df.columns:
            st.line_chart(df[['Close']])

        latest = df.iloc[-1]
        if latest['Buy']:
            st.success("📥 BUY Signal")
        elif latest['Sell']:
            st.error("📤 SELL Signal")
        else:
            st.info("⏸ No signal right now.")

    except Exception as e:
        st.error(f"❌ Failed to process {symbol}: {e}")
