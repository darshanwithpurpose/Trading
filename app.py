import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# User input
ticker = st.text_input("Enter ticker symbol", "AAPL")
data = yf.download(ticker, period="200d", interval="1d")

if not data.empty:
    # Calculate indicators
    data['High_125'] = data['High'].rolling(window=125).max()
    data['SMA_Volume_125'] = data['Volume'].rolling(window=125).mean()
    data['RSI_14'] = ta.momentum.RSIIndicator(close=data['Close'], window=14).rsi()

    # Shift by 1 day for "1 day ago" conditions
    data['High_125_1d_ago'] = data['High_125'].shift(1)
    data['SMA_Vol_1d_ago'] = data['SMA_Volume_125'].shift(1)

    # Latest data
    latest = data.iloc[-1]
    prev = data.iloc[-2]  # For 1-day-ago calculations

    # Trading condition logic
    condition_1 = latest['Close'] > max(prev['High_125_1d_ago'], latest['High'])
    condition_2 = latest['Volume'] > 2 * prev['SMA_Vol_1d_ago']
    condition_3 = latest['RSI_14'] < 70

    if condition_1 and condition_2 and condition_3:
        st.success(f"✅ BUY SIGNAL for {ticker}")
    else:
        st.warning(f"⚠️ No valid signal for {ticker} based on current criteria")

    st.dataframe(data.tail(10))
