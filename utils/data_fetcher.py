# kotegawa_screener/utils/data_fetcher.py

import yfinance as yf
import pandas as pd

def fetch_intraday_data(symbol, tf):
    tf_map = {"5m": "5m", "15m": "15m"}
    try:
        if symbol in ["NIFTY", "BANKNIFTY"]:
            ticker = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"
        else:
            ticker = symbol + ".NS"

        df = yf.download(ticker, period="1d", interval=tf_map[tf], progress=False)
        if df.empty:
            return None
        df.dropna(inplace=True)
        df['symbol'] = symbol
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
