import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# Function to get live Nifty 50 symbols from NSE website
@st.cache_data
def get_nifty50_symbols():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
        df = pd.read_csv(url)
        symbols = df['Symbol'].tolist()
        return symbols
    except Exception as e:
        st.error("⚠️ Failed to load Nifty50 symbols from NSE.")
        return []

# RSI Calculation
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD Calculation
def calculate_macd(data):
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# Strategy Logic
def generate_signals(df):
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['Signal'] = calculate_macd(df)
    df['Buy'] = (df['RSI'] < 30) & (df['MACD'] > df['Signal'])
    df['Sell'] = (df['RSI'] > 70) & (df['MACD'] < df['Signal'])
    return df

# App UI
st.title("📈 Nifty 50 Buy/Sell Signal App")
st.write("Strategy: RSI < 30 and MACD > Signal = 📥 BUY | RSI > 70 and MACD < Signal = 📤 SELL")

# Get symbols
nifty_symbols = get_nifty50_symbols()
if not nifty_symbols:
    st.stop()

selected_symbols = st.multiselect("Select stocks to scan", nifty_symbols, default=nifty_symbols[:5])
start_date = datetime.today() - timedelta(days=30)

for symbol in selected_symbols:
    st.subheader(f"📊 {symbol}")
    try:
        df = yf.download(f"{symbol}.NS", start=start_date)
        if df.empty:
            st.warning(f"No data for {symbol}")
            continue

        df = generate_signals(df)

        # Plot
        st.line_chart(df[['Close']])

        # Show signals
        recent = df.tail(5)
        if recent['Buy'].iloc[-1]:
            st.success("📥 BUY signal detected!")
        elif recent['Sell'].iloc[-1]:
            st.error("📤 SELL signal detected!")
        else:
            st.info("➖ No signal currently.")
    except Exception as e:
        st.warning(f"Error fetching data for {symbol}: {e}")
