import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 Nifty 500 Breakout Scanner — Elite 7 Filter Strategy")

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
RISK_REWARD = st.sidebar.selectbox("Risk-Reward Ratio", [1, 1.5, 2], index=2)

results_today = []
historical_details = []

for ticker in tickers:
    try:
        df = download_data(ticker)
        if df.empty or not {"Close", "High", "Low", "Volume"}.issubset(df.columns) or len(df) < 300:
            continue

        df = df.copy()

        df['High_125'] = df['High'].rolling(125).max()
        df['SMA_Volume_125'] = df['Volume'].rolling(125).mean()
        df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()
        df['ATR_Ratio'] = df['ATR'] / df['Close']
        df['EMA_200'] = df['Close'].ewm(span=200).mean()
        df['EMA_10'] = df['Close'].ewm(span=10).mean()
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], 14)
        df['ADX'] = adx.adx()
        bb = ta.volatility.BollingerBands(df['Close'], 20, 2)
        df['BB_upper'] = bb.bollinger_hband()

        anchor_low = df['Low'].rolling(20).min()
        anchored_vwap = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['VWAP_Anchor'] = anchored_vwap.where(df['Low'] == anchor_low)
        df['VWAP_Anchor'].fillna(method='ffill', inplace=True)

        df.dropna(inplace=True)

        # Full Historical Scan (last 10 years)
        for i in range(125, len(df)-5):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            conds = [
                row['Close'] > max(prev_row['High_125'], row['High']),
                row['Volume'] > 2 * prev_row['SMA_Volume_125'],
                40 < row['RSI_14'] < 70,
                row['ADX'] > 20,
                row['Close'] > row['VWAP_Anchor'],
                abs(row['Close'] - row['EMA_10']) < 0.02 * row['Close'],
                row['Close'] > row['EMA_200']
            ]
            if all(conds):
                match_date = df.index[i].date()
                historical_details.append({"Ticker": ticker, "Date Matched": match_date})
                break

        # Today's scan
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        conds_today = [
            latest['Close'] > max(prev['High_125'], latest['High']),
            latest['Volume'] > 2 * prev['SMA_Volume_125'],
            40 < latest['RSI_14'] < 70,
            latest['ADX'] > 20,
            latest['Close'] > latest['VWAP_Anchor'],
            abs(latest['Close'] - latest['EMA_10']) < 0.02 * latest['Close'],
            latest['Close'] > latest['EMA_200']
        ]

        if all(conds_today):
            entry = latest['Close']
            atr = latest['ATR']
            sl = entry - atr
            tp = entry + atr * RISK_REWARD

            future = df.iloc[-5:]
            outcome = "Open"
            for i in range(len(future)):
                if future.iloc[i]['Low'] <= sl:
                    outcome = "SL"
                    break
                elif future.iloc[i]['High'] >= tp:
                    outcome = "TP"
                    break

            results_today.append({
                "Ticker": ticker,
                "Entry": round(entry, 2),
                "SL": round(sl, 2),
                "TP": round(tp, 2),
                "RSI": round(latest['RSI_14'], 2),
                "ATR%": round(latest['ATR_Ratio'] * 100, 2),
                "ADX": round(latest['ADX'], 2),
                "Outcome": outcome
            })
    except Exception:
        continue

# Show results
if results_today:
    st.success(f"✅ {len(results_today)} stocks matched Elite 7 strategy today")
    df_today = pd.DataFrame(results_today)
    winrate = (df_today['Outcome'] == "TP").mean() * 100
    st.metric("🎯 Simulated Win Rate", f"{winrate:.1f}%")
    st.subheader("📊 Today's Matches")
    st.dataframe(df_today.sort_values(by='ATR%', ascending=False).reset_index(drop=True))
else:
    st.warning("No trade setups matched Elite 7 strategy today.")

if historical_details:
    st.subheader("📆 Stocks that matched Elite 7 in the last 10 years")
    df_hist = pd.DataFrame(historical_details)
    st.dataframe(df_hist.sort_values(by="Date Matched", ascending=False).reset_index(drop=True))
else:
    st.info("No matches found over the past 10 years across all 500 Nifty stocks.")
