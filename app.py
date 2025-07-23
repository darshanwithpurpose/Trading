# kotegawa_screener/app.py

import streamlit as st
import pandas as pd
import requests
import csv
from io import StringIO
import yfinance as yf
from datetime import datetime, timedelta
from scanner import run_screener
from utils.chart_plotter import plot_chart_with_signals


st.set_page_config(page_title="Kotegawa Screener", layout="wide")
st.title("📈 Kotegawa Screener – Intraday & 5-Day Swing")

@st.cache_data
def load_nifty500_symbols():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return df["Symbol"].dropna().unique().tolist()
    except Exception as e:
        st.error("Failed to fetch Nifty 500 symbols: " + str(e))
        return []

# Candle pattern checks
def is_bullish_engulfing(prev, curr):
    return (
        prev["Close"] < prev["Open"] and
        curr["Close"] > curr["Open"] and
        curr["Open"] < prev["Close"] and
        curr["Close"] > prev["Open"]
    )

def is_hammer(candle):
    body = abs(candle["Close"] - candle["Open"])
    lower_wick = min(candle["Open"], candle["Close"]) - candle["Low"]
    upper_wick = candle["High"] - max(candle["Open"], candle["Close"])
    return lower_wick > 2 * body and upper_wick < body

mode = st.radio("Select Mode", ["Live Intraday Screener", "Live 5-Day Swing Screener"])

if mode == "Live Intraday Screener":
    use_nifty500 = st.checkbox("Use Nifty 500 Stocks", value=True)
    if use_nifty500:
        targets = load_nifty500_symbols()
    else:
        symbols_input = st.text_input("Enter comma-separated stock symbols", value="BANKNIFTY")
        targets = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

    timeframe = st.selectbox("Select Candle Timeframe", ["5m", "15m"], index=0)

    if st.button("⏩ Run Intraday Screener"):
        results = run_screener(targets, timeframe)
        if results.empty:
            st.warning("No setups found based on Kotegawa rules today.")
        else:
            st.dataframe(results)
            for symbol in results['Stock'].unique():
                st.pyplot(plot_chart_with_signals(symbol, timeframe))

elif mode == "Live 5-Day Swing Screener":
    symbols = load_nifty500_symbols()
    st.write("Symbols Loaded:", len(symbols))
    if st.button("🔍 Run Live 5-Day Screener"):
        results = []
        with st.spinner("Scanning daily Kotegawa-style swing setups..."):
            for symbol in symbols:
                try:
                    ticker = symbol if ".NS" in symbol else symbol + ".NS"
                    df = yf.download(ticker, period="30d", interval="1d", progress=False)
                    df.dropna(inplace=True)

                    if len(df) < 21:
                        continue

                    df["SMA_20"] = df["Close"].rolling(20).mean()
                    last5 = df.iloc[-6:-1]
                    today = df.iloc[-1]
                    prev = df.iloc[-2]

                    high_5d = last5["High"].max()
                    avg_vol = last5["Volume"].mean()
                    breakout = today["Close"] > high_5d
                    high_volume = today["Volume"] > avg_vol
                    bullish_pattern = is_bullish_engulfing(prev, today) or is_hammer(today)
                    above_sma = today["Close"] > today["SMA_20"]

                    if breakout and high_volume and bullish_pattern and above_sma:
                        results.append({
                            "Symbol": symbol,
                            "Date": today.name.date(),
                            "Close": round(today["Close"], 2),
                            "Volume": int(today["Volume"]),
                            "Breakout Above": round(high_5d, 2),
                            "SMA_20": round(today["SMA_20"], 2)
                        })

                except Exception as e:
                    st.warning(f"{symbol}: {e}")

        if results:
            st.success(f"{len(results)} swing setups found.")
            st.dataframe(pd.DataFrame(results))
        else:
            st.info("No stocks met Kotegawa 5-day swing criteria today.")
