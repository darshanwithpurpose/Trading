import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import datetime

# App settings
st.set_page_config(page_title="AI Stock Predictor", layout="centered")
st.title("📈 AI Stock Predictor for Indian Market")
st.markdown("Predict the **next day's closing price** using AI and technical indicators.")

# User Input: Stock Symbol
ticker = st.text_input("Enter NSE stock symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")

# Always use latest 1 year of data
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365)
st.caption(f"📅 Using data from **{start_date}** to **{end_date}**")

# Prediction trigger
if st.button("🔮 Predict Closing Price"):
    with st.spinner("Fetching data and running model..."):
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("❌ No data found. Check stock symbol.")
        else:
            try:
                # Technical Indicators
                data['MA7'] = data['Close'].rolling(window=7).mean()
                data['MA21'] = data['Close'].rolling(window=21).mean()

                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))

                # Target column
                data['Target'] = data['Close'].shift(-1)

                # Final dataset
                features = ['Close', 'MA7', 'MA21', 'RSI', 'Volume']
                data = data[features + ['Target']].replace([np.inf, -np.inf], np.nan).dropna()

                X = data[features]
                y = data['Target']

                # Train model
                model = LinearRegression()
                model.fit(X, y)
                prediction = model.predict(X)

                # Plot result
                st.subheader("📊 Actual vs Predicted Closing Price")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(y.values, label="Actual", color='blue')
                ax.plot(prediction, label="Predicted", color='orange')
                ax.set_xlabel("Days")
                ax.set_ylabel("Price (INR)")
                ax.legend()
                st.pyplot(fig)

                # Final predicted price
                st.subheader("🔮 Predicted Next Close Price")
                st.success(f"📌 ₹{prediction[-1]:.2f} (Based on latest available data)")

                # Show last date used
