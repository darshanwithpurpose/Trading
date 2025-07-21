import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("📈 Trading Signal Scanner")

# User input
ticker = st.text_input("Enter ticker symbol", "AAPL")

if ticker:
    try:
        data = yf.download(ticker, period="200d", interval="1d", progress=False)

        # Debug: Show available columns
        st.write("Fetched columns:", data.columns.tolist())

        # Check required columns
        required_cols = {"Close", "High", "Volume"}
        if data.empty:
            st.error("❌ No data fetched. Please check the ticker symbol or your internet connection.")
        elif not required_cols.issubset(data.columns):
            st.error("❌ Required columns not found in the data. Raw data might be malformed.")
            st.dataframe(data.head())
        elif len(data) < 130:
            st.warning("⚠️ Not enough data to compute 125-day indicators. Try a longer time range.")
        else:
            # Clean & calculate indicators
            data['High_125'] = data['High'].rolling(window=125).max()
            data['SMA_Volume_125'] = data['Volume'].rolling(window=125).mean()
            rsi = ta.momentum.RSIIndicator(close=data['Close'].fillna(method='ffill'), window=14)
            data['RSI_14'] = rsi.rsi()

            data['High_125_1d_ago'] = data['High_125'].shift(1)
            data['SMA_Vol_1d_ago'] = data['SMA_Volume_125'].shift(1)

            data.dropna(inplace=True)

            latest = data.iloc[-1]
            prev = data.iloc[-2]

            condition_1 = latest['Close'] > max(prev['High_125_1d_ago'], latest['High'])
            condition_2 = latest['Volume'] > 2 * prev['SMA_Vol_1d_ago']
            condition_3 = latest['RSI_14'] < 70

            if condition_1 and condition_2 and condition_3:
                st.success(f"✅ BUY SIGNAL for {ticker}")
            else:
                st.warning(f"⚠️ No signal for {ticker} based on criteria")

            st.subheader("🔍 Latest Data")
            st.dataframe(data.tail(10))
    except Exception as e:
        st.exception(f"Unhandled error: {e}")
