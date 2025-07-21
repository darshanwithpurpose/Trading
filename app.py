import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("🇮🇳 Nifty 500 Trading Signal Scanner (No External Modules)")

@st.cache_data
def get_nifty500_symbols():
    url = "https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE500&opttopic=indexcomp&index=34"
    tables = pd.read_html(url)
    df = tables[0]
    symbols = df['Company'].tolist()
    codes = df['Symbol'].tolist()
    return [code.strip() + ".NS" for code in codes if isinstance(code, str)]

tickers = get_nifty500_symbols()

MAX_TICKERS = st.sidebar.slider("🔢 Max tickers to scan", 10, 500, 50)
tickers = tickers[:MAX_TICKERS]

results = []

for ticker in tickers:
    try:
        data = yf.download(ticker, period="200d", interval="1d", progress=False)
        if data.empty or not {"Close", "High", "Volume"}.issubset(data.columns) or len(data) < 130:
            continue

        data['High_125'] = data['High'].rolling(125).max()
        data['SMA_Vol_125'] = data['Volume'].rolling(125).mean()
        data['RSI_14'] = ta.momentum.RSIIndicator(
            close=data['Close'].fillna(method='ffill'), window=14
        ).rsi()
        data['High_125_1d'] = data['High_125'].shift(1)
        data['SMA_Vol_1d'] = data['SMA_Vol_125'].shift(1)
        data.dropna(inplace=True)

        latest = data.iloc[-1]
        prev = data.iloc[-2]

        if (
            latest['Close'] > max(prev['High_125_1d'], latest['High']) and
            latest['Volume'] > 2 * prev['SMA_Vol_1d'] and
            latest['RSI_14'] < 70
        ):
            results.append({
                "Ticker": ticker,
                "Close": latest['Close'],
                "Volume": latest['Volume'],
                "RSI_14": round(latest['RSI_14'], 2)
            })
    except Exception:
        continue

if results:
    st.success(f"✅ {len(results)} stocks meet the buy condition.")
    st.dataframe(pd.DataFrame(results))
else:
    st.warning("🚫 No buy signals found today.")
