# kotegawa_screener/app.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from scanner import run_screener
from utils.chart_plotter import plot_chart_with_signals
from backtest_eod import backtest_kotegawa_daily

st.set_page_config(page_title="Kotegawa Swing Backtester", layout="wide")
st.title("📈 Kotegawa 5-Day Swing Backtester (Indian Market)")

st.markdown("""
### ⏱️ Timeframe Strategy Guide

| Timeframe | Use Case | Pros | Cons |
|----------|----------|------|------|
| **5-Day**  | 🧭 Swing Trading | Fewer but stronger signals, higher reward | Longer holding period |

#### ✅ Recommendations:
- **5-Day Setup:** Use daily candles and look for breakout or reversal from 5-day consolidation zones  

#### 📌 Buy & Sell Rules (5-Day Swing):
- **Buy:** Daily close breaks above last 5-day high with volume confirmation  
- **Stoploss:** Recent 5-day low  
- **Target:** 1.5x reward-to-risk from entry
""")

@st.cache_data
def load_nifty500_symbols():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return df['Symbol'].dropna().unique().tolist()
    except Exception as e:
        st.error("Failed to fetch Nifty 500 symbols: " + str(e))
        return []

# Only Backtest Mode shown
mode = st.radio("Select Mode", ["5-Day Swing Backtest"])

if mode == "5-Day Swing Backtest":
    symbols = load_nifty500_symbols()
    st.write("Symbols Loaded:", len(symbols))
    st.write(symbols[:10])

    start_date = (date.today() - timedelta(days=3 * 365)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    if st.button("🔍 Run Backtest for All Nifty 500 (5-Day Setup)"):
        results = []
        with st.spinner("Running backtests... this may take several minutes."):
            for symbol in symbols:
                st.write(f"Backtesting {symbol}...")
                df = backtest_kotegawa_daily(symbol, start=start_date, end=end_date, mode="5d")
                if not df.empty and "Error" not in df.columns:
                    df["Symbol"] = symbol
                    results.append(df)
                elif "Error" in df.columns:
                    st.error(f"{symbol}: {df['Error'].iloc[0]}")

        if results:
            final = pd.concat(results)
            st.dataframe(final[['Symbol', 'Date', 'Entry', 'Target', 'SL', 'ExitPrice', 'Outcome']])
            st.metric("Total Trades", len(final))
            st.metric("Successful Trades", (final['Outcome'] == 'HIT_TARGET').sum())
            st.metric("Failed Trades", (final['Outcome'] == 'HIT_SL').sum())
        else:
            st.warning("No valid backtest results from Nifty 500 symbols.")
