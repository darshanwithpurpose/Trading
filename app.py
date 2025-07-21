import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta

st.title("NSE Candlestick Pattern Profit Detector 📊")

stock = st.text_input("Enter NSE stock symbol (e.g., INFY.NS)", "RELIANCE.NS")
start_date = st.date_input("Start Date", datetime.today() - timedelta(days=365))
end_date = st.date_input("End Date", datetime.today())

def is_hammer(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Open'] - candle['Low'] if candle['Close'] > candle['Open'] else candle['Close'] - candle['Low']
    upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
    return lower_shadow > 2 * body and upper_shadow < 0.3 * body

def is_doji(candle):
    return abs(candle['Open'] - candle['Close']) <= (0.1 * (candle['High'] - candle['Low']))

def is_inverted_hammer(candle):
    body = abs(candle['Close'] - candle['Open'])
    upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
    lower_shadow = min(candle['Close'], candle['Open']) - candle['Low']
    return upper_shadow > 2 * body and lower_shadow < 0.3 * body

def find_swing_low(df, i):
    return df['Low'][i] < df['Low'][i - 2] and df['Low'][i] < df['Low'][i - 1] and df['Low'][i] < df['Low'][i + 1] and df['Low'][i] < df['Low'][i + 2]

def find_swing_high(df, i):
    return df['High'][i] > df['High'][i - 2] and df['High'][i] > df['High'][i - 1] and df['High'][i] > df['High'][i + 1] and df['High'][i] > df['High'][i + 2]

@st.cache_data
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    df.dropna(inplace=True)
    return df

df = load_data(stock, start_date, end_date)

signals = []
for i in range(2, len(df) - 2):
    candle = df.iloc[i]
    next_candle = df.iloc[i + 1]

    if find_swing_low(df, i):
        if is_hammer(candle) and next_candle['Close'] > candle['Close']:
            signals.append({'Date': df.index[i], 'Type': 'Buy', 'Pattern': 'Hammer'})
        elif is_doji(candle) and next_candle['Close'] > candle['Close']:
            signals.append({'Date': df.index[i], 'Type': 'Buy', 'Pattern': 'Doji'})
        elif is_inverted_hammer(candle) and next_candle['Close'] > candle['Close']:
            signals.append({'Date': df.index[i], 'Type': 'Buy', 'Pattern': 'Inverted Hammer'})

    if find_swing_high(df, i):
        if is_doji(candle) and next_candle['Close'] < candle['Close']:
            signals.append({'Date': df.index[i], 'Type': 'Sell', 'Pattern': 'Doji'})

signal_df = pd.DataFrame(signals)

st.subheader("Trade Signals (Based on Pattern Detection)")
st.dataframe(signal_df)

if not signal_df.empty:
    st.success(f"Total profitable signals found: {len(signal_df)}")
else:
    st.warning("No patterns matched the criteria in this date range.")
