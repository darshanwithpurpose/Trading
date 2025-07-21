import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 Nifty 500 Breakout Scanner — Simplified Breakout")

@st.cache_data(show_spinner=False)
def get_nifty500_symbols():
    url = "https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE500&opttopic=indexcomp&index=34"
    tables = pd.read_html(url)
    df = tables[0]
    if "Symbol" in df.columns:
        return [sym.strip() + ".NS" for sym in df["Symbol"].dropna()]
    else:
        return [sym.strip() + ".NS" for sym in df.iloc[:, 1].dropna()]

@st.cache_data(show_spinner=False)
def download_data(ticker):
    return yf.download(ticker, period="3y", interval="1d", progress=False)

tickers = get_nifty500_symbols()[:500]

results_today = []
historical_details = []
condition_matrix = []

pass_counts = {
    "High Breakout": 0,
    "Volume > SMA": 0,
    "Close > EMA_150": 0,
    "Total": 0
}

for ticker in tickers:
    try:
        df = download_data(ticker)
        if df.empty or not {"Close", "High", "Low", "Volume"}.issubset(df.columns) or len(df) < 150:
            continue

        df = df.copy()
        df['High_100'] = df['High'].rolling(100).max().shift(1)
        df['SMA_Volume_30'] = df['Volume'].rolling(30).mean()
        df['EMA_150'] = df['Close'].ewm(span=150).mean()
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
        df['ATR_Ratio'] = df['ATR'] / df['Close']

        df.dropna(inplace=True)

        for i in range(150, len(df)-5):
            row = df.iloc[i]
            conds = [
                row['High'] > row['High_100'],
                row['Volume'] > row['SMA_Volume_30'],
                row['Close'] > row['EMA_150']
            ]
            if all(conds):
                match_date = df.index[i].date()
                historical_details.append({"Ticker": ticker, "Date Matched": match_date})
                break

        latest = df.iloc[-1]
        conds_today = [
            latest['High'] > latest['High_100'],
            latest['Volume'] > latest['SMA_Volume_30'],
            latest['Close'] > latest['EMA_150']
        ]

        pass_counts["Total"] += 1
        pass_counts["High Breakout"] += int(conds_today[0])
        pass_counts["Volume > SMA"] += int(conds_today[1])
        pass_counts["Close > EMA_150"] += int(conds_today[2])

        condition_matrix.append({
            "Ticker": ticker,
            "High > High_100": conds_today[0],
            "Volume > SMA": conds_today[1],
            "Close > EMA_150": conds_today[2]
        })

        if all(conds_today):
            results_today.append({
                "Ticker": ticker,
                "Close": round(latest['Close'], 2),
                "ATR%": round(latest['ATR_Ratio'] * 100, 2)
            })
    except Exception:
        continue

if results_today:
    st.success(f"✅ {len(results_today)} stocks matched Simplified Breakout strategy today")
    df_today = pd.DataFrame(results_today)
    st.subheader("📊 Today's Matches")
    st.dataframe(df_today.sort_values(by='ATR%', ascending=False).reset_index(drop=True))
else:
    st.warning("No trade setups matched Simplified Breakout strategy today.")

if historical_details:
    st.subheader("📆 Stocks that matched Simplified Breakout strategy in the last 3 years")
    df_hist = pd.DataFrame(historical_details)
    st.dataframe(df_hist.sort_values(by="Date Matched", ascending=False).reset_index(drop=True))
else:
    st.info("No matches found over the past 3 years across all 500 Nifty stocks.")

if condition_matrix:
    st.subheader("🔍 Condition Matrix for Today")
    df_cond = pd.DataFrame(condition_matrix)
    st.dataframe(df_cond)

st.subheader("📊 Condition Pass Rate")
total_checked = pass_counts["Total"] if pass_counts["Total"] > 0 else 1
pass_df = pd.DataFrame({
    "Condition": ["High Breakout", "Volume > SMA", "Close > EMA_150"],
    "% Passed": [
        round(100 * pass_counts[k] / total_checked, 2) for k in ["High Breakout", "Volume > SMA", "Close > EMA_150"]
    ]
})
st.dataframe(pass_df)
