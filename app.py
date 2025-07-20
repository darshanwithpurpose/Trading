import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import datetime

# Streamlit config
st.set_page_config(page_title="AI Stock Predictor", layout="centered")
st.title("📈 AI Stock Predictor for Indian Market")
st.markdown("Predict the **next day's closing price** and see buy/sell signals based on moving averages.")

# Input
ticker = st.text_input("Enter NSE stock symbol (e.g., RELIANCE.NS):", "RELIANCE.NS")

# Date range
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365)
st.caption(f"📅 Using data from **{start_date}** to **{end_date}**")

if st.button("🔮 Predict & Recommend"):
    with st.spinner("Fetching data and running model..."):
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("❌ No data found. Please check the stock symbol.")
        else:
            try:
                # Technical indicators
                data['MA7'] = data['Close'].rolling(window=7).mean()
                data['MA21'] = data['Close'].rolling(window=21).mean()

                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                data['RSI'] = 100 - (100 / (1 + rs))

                # Target: next day close
                data['Target'] = data['Close'].shift(-1)

                # Features
                features = ['Close', 'MA7', 'MA21', 'RSI', 'Volume']
                data = data[features + ['Target']].replace([np.inf, -np.inf], np.nan).dropna()

                X = data[features]
                y = data['Target']

                # Train model
                model = LinearRegression()
                model.fit(X, y)
                prediction = model.predict(X)

                # Plot: Actual vs Predicted
                st.subheader("📊 Actual vs Predicted Closing Price")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(y.values, label="Actual", color='blue')
                ax.plot(prediction, label="Predicted", color='orange')
                ax.set_xlabel("Days")
                ax.set_ylabel("Price (INR)")
                ax.legend()
                st.pyplot(fig)

                # Final prediction
                st.subheader("🔮 Predicted Next Close Price")
                st.success(f"📌 ₹{prediction[-1]:.2f} (based on latest data)")
                st.caption(f"✅ Latest trading date: {data.index[-1].strftime('%Y-%m-%d')}")

                # ---- 🟢 Buy / 🔴 Sell Signal Logic ----
                st.subheader("📌 Buy / Sell Recommendations (Next 1 Month Approx.)")

                data_signals = data.copy()
                data_signals['Signal'] = 0
                data_signals['Signal'][data_signals['MA7'] > data_signals['MA21']] = 1
                data_signals['Position'] = data_signals['Signal'].diff()

                # Show only last 20 signals (approx. 1 month of trading)
                last_20 = data_signals.tail(60)  # more days to catch crossover within 20 days

                buy_signals = last_20[last_20['Position'] == 1.0]
                sell_signals = last_20[last_20['Position'] == -1.0]

                st.write("🟢 **Buy Dates & Prices**:")
                if not buy_signals.empty:
                    st.dataframe(buy_signals[['Close']].rename(columns={'Close': 'Buy Price'}))
                else:
                    st.info("No Buy signal in the last 1 month window.")

                st.write("🔴 **Sell Dates & Prices**:")
                if not sell_signals.empty:
                    st.dataframe(sell_signals[['Close']].rename(columns={'Close': 'Sell Price'}))
                else:
                    st.info("No Sell signal in the last 1 month window.")

            except Exception as e:
                st.error(f"🚫 Error: {str(e)}")
