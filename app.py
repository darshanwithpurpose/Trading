import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

st.title("📈 AI Stock Predictor for Indian Market")
st.markdown("Predict the next day's closing price with simple machine learning.")

ticker = st.text_input("Enter NSE stock symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")
start_date = st.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End date", pd.to_datetime("2024-12-31"))

if st.button("Predict"):
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        st.error("⚠️ Invalid symbol or no data found.")
    else:
        # Indicators
        data['MA7'] = data['Close'].rolling(window=7).mean()
        data['MA21'] = data['Close'].rolling(window=21).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        data['Target'] = data['Close'].shift(-1)
        data.dropna(inplace=True)
        
        features = ['Close', 'MA7', 'MA21', 'RSI', 'Volume']
        X = data[features]
        y = data['Target']

        model = LinearRegression()
        model.fit(X, y)
        prediction = model.predict(X)

        # Output
        st.subheader("📉 Actual vs Predicted Closing Price")
        plt.figure(figsize=(10, 5))
        plt.plot(y.values, label="Actual")
        plt.plot(prediction, label="Predicted")
        plt.legend()
        st.pyplot(plt)

        st.subheader("🔮 Next Day Prediction")
        st.write(f"Predicted Closing Price: ₹{prediction[-1]:.2f}")
