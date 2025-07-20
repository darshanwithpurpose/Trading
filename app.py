import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Stock Predictor", layout="centered")
st.title("📈 AI Stock Predictor for Indian Market")
st.markdown("Predict the **next day's closing price** using simple machine learning and technical indicators.")

# Input section
ticker = st.text_input("Enter NSE stock symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
start_date = st.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End date", pd.to_datetime("2024-12-31"))

if st.button("🔮 Predict Closing Price"):
    with st.spinner("Fetching data and predicting..."):
        try:
            data = yf.download(ticker, start=start_date, end=end_date)

            if data.empty:
                st.error("⚠️ No data found. Please check the symbol or date range.")
            else:
                # --- Add Technical Indicators ---
                data['MA7'] = data['Close'].rolling(window=7).mean()
                data['MA21'] = data['Close'].rolling(window=21).mean()

                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))

                # Target: Next da
