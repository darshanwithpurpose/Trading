import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ----------------------------------------
# Utility: Fetch Nifty50 symbols from NSE
# ----------------------------------------
@st.cache_data
def get_nifty50_symbols():
    url = "https://www1.nseindia.com/content/indices/ind_nifty50list.csv"
    try:
        df = pd.read_csv(url)
        symbols = df["Symbol"].tolist()
        return [symbol + ".NS" for symbol in symbols]
    except Exception as e:
        st.error("Failed to load Nifty50 symbols from NSE.")
        return ["RELIANCE.NS", "TCS.NS", "INFY.NS"]  # fallback

# ----------------------------------------
# Fetch stock data and calculate indicators
# ----------------------------------------
def fetch_data(symbol, period="3mo"):
    df = yf.download(symbol, period=period)
    if df.empty:
        st.warning(f"No data returned for {symbol}")
        return pd.DataFrame()
    
    df["MA7"] = df["Close"].rolling(window=7).mean()
    df["MA21"] = df["Close"].rolling(window=21).mean()

    df["Signal"] = ["Buy" if m7 > m21 else "Sell" for m7, m21 in zip(df["MA7"].fillna(0), df["MA21"].fillna(0))]
    return df

# ----------------------------------------
# Streamlit UI starts here
# ----------------------------------------
st.set_page_config(page_title="📈 AI Stock Advisor", layout="wide")
st.title("🇮🇳 AI-Powered Indian Stock Advisor (Nifty 50)")

# Load list of stocks
symbols = get_nifty50_symbols()
selected_stock = st.selectbox("🔍 Select a Stock", symbols)

# Fetch and display data
df = fetch_data(selected_stock)

if not df.empty:
    st.subheader(f"📅 Data from {df.index.min().date()} to {df.index.max().date()}")
    
    # Line chart: Close + MA
    plot_cols = ["Close"]
    if "MA7" in df.columns and "MA21" in df.columns:
        plot_cols.extend(["MA7", "MA21"])
    st.line_chart(df[plot_cols])

    # Show latest recommendation
    latest_signal = df["Signal"].iloc[-1]
    st.success(f"📊 **Latest Signal: {latest_signal}** for {selected_stock}")

    # Buy/Sell Summary for 1-month
    st.subheader("🗓️ Last 1 Month Recommendations")
    one_month_ago = df.index.max() - pd.DateOffset(days=30)
    df_month = df[df.index >= one_month_ago]
    if not df_month.empty:
        buy_days = df_month[df_month["Signal"] == "Buy"]
        sell_days = df_month[df_month["Signal"] == "Sell"]
        st.markdown(f"✅ **Buy days:** {len(buy_days)}")
        st.markdown(f"❌ **Sell days:** {len(sell_days)}")
    else:
        st.info("Not enough data for 1-month analysis.")

else:
    st.error("No data to show for this stock.")
