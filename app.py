import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 Nifty 500 Breakout Scanner with Backtesting")

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
    return yf.download(ticker, period="400d", interval="1d", progress=False)

# Parameters
MAX_TICKERS = st.sidebar.slider("🔢 Max stocks to scan", 10, 500, 50)
RISK_REWARD = st.sidebar.selectbox("Risk-Reward Ratio", [1, 1.5, 2], index=2)

tickers = get_nifty500_symbols()[:MAX_TICKERS]
results = []

for ticker in tickers:
    try:
        df = download_data(ticker)
        if df.empty or not {"Close", "High", "Low", "Volume"}.issubset(df.columns) or len(df) < 200:
            continue

        df = df.copy()

        # Indicators
        df['High_125'] = df['High'].rolling(125).max()
        df['SMA_Volume_125'] = df['Volume'].rolling(125).mean()
        df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
        df['ATR_Ratio'] = df['ATR'] / df['Close']
        df['EMA_200'] = df['Close'].ewm(span=200).mean()
        bb = ta.volatility.BollingerBands(df['Close'], 20, 2)
        df['BB_upper'] = bb.bollinger_hband()

        df.dropna(inplace=True)
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Conditions
        cond1 = latest['Close'] > max(prev['High_125'], latest['High'])
        cond2 = latest['Volume'] > 2 * prev['SMA_Volume_125']
        cond3 = 40 < latest['RSI_14'] < 70
        cond4 = latest['ATR_Ratio'] > 0.015
        cond5 = latest['Close'] > latest['BB_upper']
        cond6 = latest['Close'] > latest['EMA_200']

        if all([cond1, cond2, cond3, cond4, cond5, cond6]):
            # Backtest simulation
            entry = latest['Close']
            atr = latest['ATR']
            sl = entry - atr
            tp = entry + atr * RISK_REWARD

            future = df.iloc[-5:]  # Simulate next 5 days
            outcome = "Open"
            for i in range(len(future)):
                if future.iloc[i]['Low'] <= sl:
                    outcome = "SL"
                    break
                elif future.iloc[i]['High'] >= tp:
                    outcome = "TP"
                    break

            results.append({
                "Ticker": ticker,
                "Entry": round(entry, 2),
                "SL": round(sl, 2),
                "TP": round(tp, 2),
                "RSI": round(latest['RSI_14'], 2),
                "ATR%": round(latest['ATR_Ratio'] * 100, 2),
                "Outcome": outcome
            })
    except Exception:
        continue

if results:
    st.success(f"✅ {len(results)} stocks matched criteria")
    df_res = pd.DataFrame(results)

    winrate = (df_res['Outcome'] == "TP").mean() * 100
    st.metric("🎯 Simulated Win Rate", f"{winrate:.1f}%")

    st.dataframe(df_res.sort_values(by='ATR%', ascending=False).reset_index(drop=True))
else:
    st.warning("No trade setups found based on current criteria.")
