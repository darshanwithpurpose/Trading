# kotegawa_screener/scanner.py

import pandas as pd
from utils.data_fetcher import fetch_intraday_data
from patterns import is_bullish_engulfing, is_hammer, near_support

def run_screener(symbols, tf):
    signals = []
    for symbol in symbols:
        df = fetch_intraday_data(symbol, tf)
        if df is None or len(df) < 15:
            continue

        for i in range(1, len(df)):
            if (is_bullish_engulfing(df.iloc[i - 1], df.iloc[i]) or is_hammer(df.iloc[i])) and \
               df['Volume'].iloc[i] > df['Volume'].rolling(10).mean().iloc[i] and \
               near_support(df.iloc[i], df):
                signals.append({
                    "Stock": symbol,
                    "Time": df.index[i],
                    "Pattern": "Reversal",
                    "Entry": df['High'].iloc[i] + 0.1,
                    "SL": df['Low'].iloc[i],
                    "Target": df['High'].iloc[i] + (df['High'].iloc[i] - df['Low'].iloc[i]) * 1.5
                })
    return pd.DataFrame(signals)
