import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("📈 Trading Signal Scanner")

# User input
ticker = st.text_input("Enter ticker symbol", "AAPL")

if ticker:
    data = yf.download(ticker, period="200d", interval="1d", progress=False)

    if data.empty:
        st.error("❌ No data fetched. Please check the ticker symbol or your internet connection.")
    elif not set(['Close', 'High', 'Volume']).issubset(data.columns):
        st.error("❌ Required columns not found in the data. Possible data fetch error.")
    elif len(data) < 130:
        st.warning("⚠️ Not enough data to compute 125-day indicators. Try a longer time range.")
    else:
        # Calculate indicators
        data['High_125'] = data['High'].rolling(window=125).max()
        data['SMA_Volume_125'] = data['Volume'].rolling(window=125).mean()

        # RSI (handle NaNs safely)
        close_filled = data['Close'].fillna(method='ffill')
        rsi_indicator = ta.momentum.RSIIndicator(close=close_filled, window=14)
        data['RSI_14'] = rsi_indicator.rsi()

        # Shift 1-day ago values
        data['High_125_1d_ago'] = data['High_125'].shift(1)
        data['SMA_Vol_1d_ago'] = data['SMA_Volume_125'].shift(1)

        # Drop NaNs after all indicators are calculated
        data.dropna(inplace=True)

        # Latest row and 1-day-ago row
        latest = data.iloc[-1]
        prev = data.iloc[-2]

        # Strategy logic
        condition_1 = latest['Close'] > max(prev['High_125_1d_ago'], latest['High'])
        condition_2 = latest['Volume'] > 2 * prev['SMA_Vol_1d_ago']
        condition_3 = latest['RSI_14'] < 70

        if condition_1 and condition_2 and condition_3:
            st.success(f"✅ BUY SIGNAL for {ticker}")
        else:
            st.warning(f"⚠️ No signal for {ticker} based on criteria")

        st.subheader("🔍 Latest Data")
        st.dataframe(data.tail(10))
