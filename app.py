import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# User input
ticker = st.text_input("Enter ticker symbol", "AAPL")
data = yf.download(ticker, period="200d", interval="1d")

if not data.empty and len(data) > 130:
    # Drop NaNs just in case
    data = data.dropna(subset=["Close", "High", "Volume"])

    # Calculate indicators
    data['High_125'] = data['High'].rolling(window=125).max()
    data['SMA_Volume_125'] = data['Volume'].rolling(window=125).mean()
    
    rsi_indicator = ta.momentum.RSIIndicator(close=data['Close'].fillna(method='ffill'), window=14)
    data['RSI_14'] = rsi_indicator.rsi()

    # Shifted values for 1-day ago
    data['High_125_1d_ago'] = data['High_125'].shift(1)
    data['SMA_Vol_1d_ago'] = data['SMA_Volume_125'].shift(1)

    # Clean NaNs
    data.dropna(inplace=True)

    # Latest data
    latest = data.iloc[-1]
    prev = data.iloc[-2]

    # Trading logic
    condition_1 = latest['Close'] > max(prev['High_125_1d_ago'], latest['High'])
    condition_2 = latest['Volume'] > 2 * prev['SMA_Vol_1d_ago']
    condition_3 = latest['RSI_14'] < 70

    if condition_1 and condition_2 and condition_3:
        st.success(f"✅ BUY SIGNAL for {ticker}")
    else:
        st.warning(f"⚠️ No valid signal for {ticker} based on current criteria")

    st.dataframe(data.tail(10))
else:
    st.error("❌ Not enough data to calculate indicators. Please try a different ticker or date range.")
