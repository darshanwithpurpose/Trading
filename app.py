import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="NIFTY 50 Stock Predictor", layout="centered")

# Title
st.title("📈 NIFTY 50 AI Stock Prediction and Signal")

# Function to get NIFTY 50 stock symbols
@st.cache_data
def get_nifty50_symbols():
    symbols = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HINDUNILVR",
        "ITC", "LT", "SBIN", "KOTAKBANK", "AXISBANK", "ASIANPAINT", "BHARTIARTL",
        "BAJFINANCE", "HCLTECH", "WIPRO", "MARUTI", "NTPC", "TITAN", "SUNPHARMA",
        "POWERGRID", "NESTLEIND", "ULTRACEMCO", "TECHM", "JSWSTEEL", "TATAMOTORS",
        "ADANIENT", "COALINDIA", "ONGC", "GRASIM", "ADANIPORTS", "HDFCLIFE", "BRITANNIA",
        "CIPLA", "DIVISLAB", "BPCL", "HINDALCO", "HEROMOTOCO", "BAJAJ-AUTO", "SBILIFE",
        "EICHERMOT", "DRREDDY", "BAJAJFINSV", "APOLLOHOSP", "INDUSINDBK", "ICICIPRULI",
        "TATACONSUM", "SHREECEM", "M&M", "UPL"
    ]
    return [symbol + ".NS" for symbol in symbols]

# Fetch historical data
@st.cache_data
def fetch_data(symbol, period="2mo"):
    df = yf.download(symbol, period=period)
    df.dropna(inplace=True)
    df["MA7"] = df["Close"].rolling(window=7).mean()
    df["MA21"] = df["Close"].rolling(window=21).mean()
    df["Signal"] = ["Buy" if m7 > m21 else "Sell" for m7, m21 in zip(df["MA7"], df["MA21"])]
    return df

# Predict next day's closing price
def predict_price(df):
    df = df.copy()
    df["Target"] = df["Close"].shift(-1)
    df.dropna(inplace=True)

    X = df[["Open", "High", "Low", "Close", "Volume"]]
    y = df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)

    prediction = model.predict([X.iloc[-1]])[0]
    return round(prediction, 2)

# UI: Select stock
nifty_symbols = get_nifty50_symbols()
selected_stock = st.selectbox("Choose a NIFTY 50 stock", nifty_symbols)

# Fetch and display data
df = fetch_data(selected_stock)
st.line_chart(df[["Close", "MA7", "MA21"]])

# Show recommendation
current_signal = df["Signal"].iloc[-1]
st.subheader(f"📊 Recommendation: **{current_signal}**")

# Predict tomorrow's price
predicted_price = predict_price(df)
st.metric("Predicted Next Close", f"₹ {predicted_price}")

# Show raw data option
if st.checkbox("Show data table"):
    st.dataframe(df.tail(30))
