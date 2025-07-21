import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 Nifty 500 Breakout Scanner — Relaxed Strategy")

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
    return yf.download(ticker, period="10y", interval="1d", progress=False)

# Always scan full Nifty 500
tickers = get_nifty500_symbols()[:500]

results_today = []
historical_details = []

for ticker in tickers:
    try:
        df = download_data(ticker)
        if df.empty or not {"Close", "High", "Low", "Volume"}.issubset(df.columns) or len(df) < 300:
            continue

        df = df.copy()

        df['High_100'] = df['High'].rolling(100).max()
        df['SMA_Volume_30'] = df['Volume'].rolling(30).mean()
        df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
        df['ATR_Ratio'] = df['ATR'] / df['Close']
        df['EMA_150'] = df['Close'].ewm(span=150).mean()
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], 14)
        df['ADX'] = adx.adx()

        df.dropna(inplace=True)

        # Full Historical Scan (last 10 years)
        for i in range(150, len(df)-5):
            row = df.iloc[i]
            conds = [
                row['Close'] > row['High_100'],
                row['Volume'] > 1.2 * row['SMA_Volume_30'],
                row['RSI_14'] < 80,
                row['ADX'] > 15,
                row['Close'] > row['EMA_150']
            ]
            if all(conds):
                match_date = df.index[i].date()
                historical_details.append({"Ticker": ticker, "Date Matched": match_date})
                break

        # Today's scan
        latest = df.iloc[-1]
        conds_today = [
            latest['Close'] > latest['High_100'],
            latest['Volume'] > 1.2 * latest['SMA_Volume_30'],
            latest['RSI_14'] < 80,
            latest['ADX'] > 15,
            latest['Close'] > latest['EMA_150']
        ]

        if all(conds_today):
            results_today.append({
                "Ticker": ticker,
                "Close": round(latest['Close'], 2),
                "RSI": round(latest['RSI_14'], 2),
                "ATR%": round(latest['ATR_Ratio'] * 100, 2),
                "ADX": round(latest['ADX'], 2)
            })
    except Exception:
        continue

# Show results
if results_today:
    st.success(f"✅ {len(results_today)} stocks matched Relaxed Strategy today")
    df_today = pd.DataFrame(results_today)
    st.subheader("📊 Today's Matches")
    st.dataframe(df_today.sort_values(by='ATR%', ascending=False).reset_index(drop=True))
else:
    st.warning("No trade setups matched Relaxed Strategy today.")

if historical_details:
    st.subheader("📆 Stocks that matched Relaxed Strategy in the last 10 years")
    df_hist = pd.DataFrame(historical_details)
    st.dataframe(df_hist.sort_values(by="Date Matched", ascending=False).reset_index(drop=True))
else:
    st.info("No matches found over the past 10 years across all 500 Nifty stocks.")
