import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

@st.cache_data
def get_nifty50_symbols():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
        df = pd.read_csv(url)
        return df['Symbol'].tolist()
    except Exception:
        return ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']  # fallback

def fetch_data(symbol, period="3mo", interval="1d"):
    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.history(period=period, interval=interval)
    df['MA7'] = df['Close'].rolling(window=7).mean()
    df['MA21'] = df['Close'].rolling(window=21).mean()
    return df

def generate_signals(df):
    df['Signal'] = ''
    for i in range(1, len(df)):
        if df['MA7'][i] > df['MA21'][i] and df['MA7'][i - 1] <= df['MA21'][i - 1]:
            df.loc[df.index[i], 'Signal'] = 'BUY'
        elif df['MA7'][i] < df['MA21'][i] and df['MA7'][i - 1] >= df['MA21'][i - 1]:
            df.loc[df.index[i], 'Signal'] = 'SELL'
    return df

# UI
st.title("📈 Nifty50 AI Trading Assistant")

symbols = get_nifty50_symbols()
selected_symbol = st.selectbox("Choose Nifty50 Stock", symbols)

data = fetch_data(selected_symbol)
data = generate_signals(data)

st.line_chart(data[["Close", "MA7", "MA21"]])

latest = data.iloc[-1]
st.write(f"### Last Close: ₹{latest['Close']:.2f}")
st.write(f"### Signal: {latest['Signal']}")

# Buy/Sell recommendation summary
buy_signals = []
sell_signals = []

for symbol in symbols:
    df = fetch_data(symbol, period="1mo")
    df = generate_signals(df)
    if df['Signal'].iloc[-1] == 'BUY':
        buy_signals.append(symbol)
    elif df['Signal'].iloc[-1] == 'SELL':
        sell_signals.append(symbol)

st.subheader("📌 Recommendations for 1-Month")
st.success(f"**Buy:** {', '.join(buy_signals)}")
st.error(f"**Sell:** {', '.join(sell_signals)}")
