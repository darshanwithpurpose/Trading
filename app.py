# kotegawa_screener/app.py

import streamlit as st
import pandas as pd
import requests
import csv
from io import StringIO
from datetime import date, timedelta
from scanner import run_screener
from utils.chart_plotter import plot_chart_with_signals
from backtest_eod import backtest_kotegawa_daily

st.set_page_config(page_title="Kotegawa Intraday Screener", layout="wide")
st.title("📈 Kotegawa-Style Screener & Backtester (Indian Market)")

@st.cache_data
def load_nifty500_symbols():
    try:
        url = "https://www1.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www1.nseindia.com"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        symbols = []
        reader = csv.DictReader(StringIO(response.text))
        for row in reader:
            symbol = row.get("Symbol")
            if symbol:
                symbols.append(symbol.strip().upper())
        return list(set(symbols))
    except Exception as e:
        st.error("Failed to fetch Nifty 500 symbols dynamically: " + str(e))
        return []

# Screener or Backtest toggle
mode = st.radio("Select Mode", ["Live Screener", "3-Year EOD Backtest"])

if mode == "Live Screener":
    use_nifty500 = st.checkbox("Use Nifty 500 Stocks", value=True)
    if use_nifty500:
        targets = load_nifty500_symbols()
    else:
        symbols_input = st.text_input("Enter comma-separated stock symbols", value="BANKNIFTY")
        targets = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

    timeframe = st.selectbox("Select Candle Timeframe", ["5m", "15m"], index=0)

    if st.button("⏩ Run Screener"):
        results = run_screener(targets, timeframe)
        if results.empty:
            st.warning("No setups found based on Kotegawa rules today.")
        else:
            st.dataframe(results)
            for symbol in results['Stock'].unique():
                st.pyplot(plot_chart_with_signals(symbol, timeframe))

elif mode == "3-Year EOD Backtest":
    symbols = load_nifty500_symbols()
    st.write("Symbols Loaded:", len(symbols))
    st.write(symbols[:10])

    start_date = (date.today() - timedelta(days=3 * 365)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    if st.button("🔍 Run Backtest for All Nifty 500"):
        results = []
        with st.spinner("Running backtests... this may take several minutes."):
            for symbol in symbols:
                st.write(f"Backtesting {symbol}...")
                df = backtest_kotegawa_daily(symbol, start=start_date, end=end_date)
                if not df.empty and "Error" not in df.columns:
                    df["Symbol"] = symbol
                    results.append(df)
                elif "Error" in df.columns:
                    st.error(f"{symbol}: {df['Error'].iloc[0]}")

        if results:
            final = pd.concat(results)
            st.dataframe(final)
            st.metric("Total Trades", len(final))
            st.metric("Hit Target", (final['Outcome'] == 'HIT_TARGET').sum())
            st.metric("Hit SL", (final['Outcome'] == 'HIT_SL').sum())
        else:
            st.warning("No valid backtest results from Nifty 500 symbols.")
