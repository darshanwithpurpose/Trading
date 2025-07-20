import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Streamlit page config
st.set_page_config(page_title="AI Stock Predictor", layout="centered")
st.title("📈 AI Stock Predictor for Indian Market")
st.markdown("Predict the **next day's closing price** using Machine Learning and technical indicators like MA & RSI.")

# User inputs
ticker = st.text_input("Enter NSE stock symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
start_date = st.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End date", pd.to_datetime("2024-12-31"))

if st.button("🔮 Predict Closing Price"):
    with st.spinner("📊 Fetching data and predicting..."):
        # Download stock data
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("❌ No data found. Please check the symbol or date range.")
        else:
            try:
                # Add technical indicators
                data['MA7'] = data['Close'].rolling(window=7).mean()
                data['MA21'] = data['Close'].rolling(window=21).mean()

                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))

                # Create target column (next day's closing price)
                data['Target'] = data['Close'].shift(-1)

                # Select features
                features = ['Close', 'MA7', 'MA21', 'RSI', 'Volume']
                data = data[features + ['Target']].replace([np.inf, -np.inf], np.nan).dropna()

                # Prepare data
                X = data[features]
                y = data['Target']

                # Train ML model
                model = LinearRegression()
                model.fit(X, y)
                prediction = model.predict(X)

                # Display results
                st.subheader("📊 Actual vs Predicted Closing Price")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(y.values, label="Actual", color='blue')
                ax.plot(prediction, label="Predicted", color='orange')
                ax.set_xlabel("Days")
                ax.set_ylabel("Price (INR)")
                ax.legend()
                st.pyplot(fig)

                st.subheader("🔮 Predicted Next Close Price")
                st.success(f"📌 ₹{prediction[-1]:.2f} (Based on the most recent available data)")

            except Exception as e:
                st.error(f"🚫 Prediction failed due to: {str(e)}")
