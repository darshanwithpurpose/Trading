import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Nifty 50 AI Buy/Sell Recommender", layout="wide")

st.title("📊 NIFTY 50 AI Buy/Sell Recommender (1-Month)")
st.markdown("This app dynamically fetches **NIFTY 50 stocks** and recommends **Buy/Sell** based on MA7 & MA21 crossover signals.")

# --- Function to get NIFTY 50 symbols ---
@st.cache_data
def get_nifty50_symbols():
    url = "https://raw.githubusercontent.com/someshkar/India-Stock-Data/main/ind_nifty50list.csv"
    df = pd.read_csv(url)
    return [symbol.strip() + ".NS" for symbol in df['Symbol']]

# --- Load symbols ---
WATCHLIST = get_nifty50_symbols()
st.success(f"✅ Loaded {len(WATCHLIST)} NIFTY 50 stocks")

# --- Define time range (1 month) ---
end_date = datetime.today()
start_date = end_date - timedelta(days=30)

# --- Buy/Sell Signal Logic ---
results = []
progress = st.progress(0)

for i, symbol in enumerate(WATCHLIST):
    progress.progress((i + 1) / len(WATCHLIST))
    try:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if data.empty or len(data) < 21:
            continue

        data['MA7'] = data['Close'].rolling(window=7).mean()
        data['MA21'] = data['Close'].rolling(window=21).mean()
        data['Signal'] = np.where(data['MA7'] > data['MA21'], 1, 0)
        data['Position'] = data['Signal'].diff()

        last_signal = data['Position'].iloc[-1]
        signal = "Buy" if last_signal == 1.0 else ("Sell" if last_signal == -1.0 else "-")
        last_price = round(data['Close'].iloc[-1], 2)

        results.append({
            "Stock": symbol.replace(".NS", ""),
            "Signal": signal,
            "Last Price (₹)": last_price,
            "Date": data.index[-1].strftime("%Y-%m-%d")
        })

    except Exception as e:
        continue

# --- Final Table ---
df_result = pd.DataFrame(results)
df_result = df_result[df_result['Signal'] != "-"].sort_values("Signal", ascending=False)

st.subheader("📋 Recommended Buy/Sell Stocks (Last 1 Month MA7/MA21 crossover)")
st.dataframe(df_result.reset_index(drop=True), use_container_width=True)

