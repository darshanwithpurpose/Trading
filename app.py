# kotegawa_screener/app.py

import streamlit as st
import pandas as pd
import requests
import yfinance as yf
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

# Candle pattern logic
def is_bullish_engulfing(prev, curr):
    return (
        float(prev["Close"]) < float(prev["Open"]) and
        float(curr["Close"]) > float(curr["Open"]) and
        float(curr["Open"]) < float(prev["Close"]) and
        float(curr["Close"]) > float(prev["Open"])
    )

def is_hammer(candle):
    open_price = float(candle["Open"])
    close_price = float(candle["Close"])
    low = float(candle["Low"])
    high = float(candle["High"])

    body = abs(close_price - open_price)
    lower_wick = min(open_price, close_price) - low
    upper_wick = high - max(open_price, close_price)

    return lower_wick > 2 * body and upper_wick < body

# Screener Mode Toggle
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

                    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
                    df["SMA_20"] = df["Close"].rolling(window=20).mean()

                    last5 = df.iloc[-6:-1]
                    today = df.iloc[-1]
                    prev = df.iloc[-2]

                    high_5d = last5["High"].max()
                    avg_vol = last5["Volume"].mean()

                    try:
                        close_price = float(today["Close"])
                        volume = float(today["Volume"])
                        sma_20 = float(today["SMA_20"])
                        breakout = close_price > float(high_5d)
                        high_volume = volume > float(avg_vol)
                        above_sma = close_price > sma_20
                        bullish_pattern = is_bullish_engulfing(prev, today) or is_hammer(today)

                        if breakout and high_volume and bullish_pattern and above_sma:
                            results.append({
                                "Symbol": symbol,
                                "Date": today.name.date(),
                                "Close": round(close_price, 2),
                                "Volume": int(volume),
                                "Breakout Above": round(high_5d, 2),
                                "SMA_20": round(sma_20, 2)
                            })
                    except Exception as inner_e:
                        st.warning(f"{symbol}: {inner_e}")

                except Exception as e:
                    st.warning(f"{symbol}: {e}")

        if results:
            df_result = pd.DataFrame(results)
            st.success(f"{len(df_result)} swing setups found.")
            st.dataframe(df_result)
        else:
            st.info("No stocks met Kotegawa 5-day swing criteria today.")
