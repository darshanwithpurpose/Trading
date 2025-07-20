import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from nsepython import nse_eq

# Utility: Get Nifty50 symbols dynamically
@st.cache_data
def get_nifty50_symbols():
    try:
        df = nse_eq("NIFTY 50")
        return df['data']['symbol']
    except:
        st.error("Failed to load Nifty50 symbols.")
        return []

# Utility: Technical Indicators
def calculate_indicators(df):
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA21'] = df['Close'].ewm(span=21).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

# Strategy Logic
def check_strategy(df):
    last = df.iloc[-1]
    buy = (
        last['EMA9'] > last['EMA21'] and
        last['MACD'] > last['Signal'] and
        last['RSI'] < 70 and last['RSI'] > 45
    )
    sell = (
        last['EMA9'] < last['EMA21'] and
        last['MACD'] < last['Signal'] and
        last['RSI'] > 70
    )
    if buy:
        return "BUY"
    elif sell:
        return "SELL"
    else:
        return "HOLD"

# Main Streamlit App
st.title("📈 Nifty 50 AI Strategy Signal App")
nifty_symbols = get_nifty50_symbols()

selected = st.multiselect("📊 Select stocks to analyze", nifty_symbols, default=nifty_symbols[:5])

end = datetime.datetime.today()
start = end - datetime.timedelta(days=30)

results = []

for symbol in selected:
    try:
        df = yf.download(symbol + ".NS", start=start, end=end)
        if df.empty: continue
        df = calculate_indicators(df)
        signal = check_strategy(df)
        results.append({
            "Stock": symbol,
            "Signal": signal,
            "Last Close": df['Close'].iloc[-1],
            "RSI": round(df['RSI'].iloc[-1], 2),
            "MACD": round(df['MACD'].iloc[-1], 2)
        })
    except Exception as e:
        st.warning(f"Error fetching {symbol}: {e}")

# Display signals
if results:
    result_df = pd.DataFrame(results)
    st.dataframe(result_df)

# Optional: Filter only BUY or SELL
filter_signal = st.selectbox("🔍 Filter by Signal", ["All", "BUY", "SELL"])
if filter_signal != "All":
    st.subheader(f"{filter_signal} Recommendations:")
    st.dataframe(result_df[result_df["Signal"] == filter_signal])
