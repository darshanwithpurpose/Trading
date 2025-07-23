# kotegawa_screener/app.py

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from scanner import run_screener
from utils.chart_plotter import plot_chart_with_signals

st.set_page_config(page_title="Kotegawa Intraday Screener", layout="wide")
st.title("📈 Kotegawa-Style Intraday Screener (Indian Market)")

# Dynamically fetch Nifty 500 symbols from NSE India
@st.cache_data
def load_nifty500_symbols():
    try:
        url = "https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=37"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "tbldata14"})
        rows = table.find_all("tr")[1:]  # skip header row
        symbols = []
        for row in rows:
            cols = row.find_all("td")
            if cols:
                symbols.append(cols[0].text.strip().upper())
        return symbols
    except Exception as e:
        st.error("Failed to fetch Nifty 500 symbols dynamically: " + str(e))
        return []

# Toggle to use Nifty 500 automatically
use_nifty500 = st.checkbox("Use Nifty 500 Stocks", value=True)

if use_nifty500:
    targets = load_nifty500_symbols()
else:
    symbols_input = st.text_input("Enter comma-separated stock symbols (e.g., BANKNIFTY,NIFTY,ADANIENT)", value="BANKNIFTY")
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
