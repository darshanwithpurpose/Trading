import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# 1. Nifty 50 static list (fallback)
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

# 2. Indicators: RSI & MACD
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = -delta.clip(upper=0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

# 3. Strategy: Buy/Sell logic
def generate_signals(df):
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['SignalLine'] = calculate_macd(df)
    df['Buy'] = (df['RSI'] < 30) & (df['MACD'] > df['SignalLine'])
    df['Sell'] = (df['RSI'] > 70) & (df['MACD'] < df['SignalLine'])
    return df.dropna()

# 4. Build the Streamlit App
st.title("📈 Nifty 50 Strategy: RSI + MACD Buy/Sell Signals")
st.write("Buy when RSI < 30 & MACD > SignalLine; Sell when RSI > 70 & MACD < SignalLine")

symbols = get_nifty50_symbols()
selected = st.multiselect("Pick stocks to scan", symbols, default=symbols[:5])

start_date = datetime.today() - timedelta(days=30)

for symbol in selected:
    st.subheader(symbol)
    df = yf.download(f"{symbol}.NS", start=start_date, progress=False)
    if df.empty:
        st.warning("No data for this stock.")
        continue

    df = generate_signals(df)
    st.line_chart(df[['Close']])

    latest = df.iloc[-1]
    if latest['Buy']:
        st.success("📥 BUY Signal!")
    elif latest['Sell']:
        st.error("📤 SELL Signal!")
    else:
        st.info("⏸ No signal right now.")
