# kotegawa_screener/scanner.py

import yfinance as yf
import pandas as pd
from patterns import is_bullish_engulfing, is_hammer

def run_screener(symbols, timeframe="5m"):
    all_signals = []

    for symbol in symbols:
        try:
            ticker = symbol if ".NS" in symbol else symbol + ".NS"
            df = yf.download(ticker, period="1d", interval=timeframe, progress=False)
            df.dropna(inplace=True)
            df.reset_index(inplace=True)

            for i in range(1, len(df)):
                prev = df.iloc[i - 1]
                curr = df.iloc[i]

                if (
                    is_bullish_engulfing(prev, curr) or is_hammer(curr)
                ) and curr["Volume"] > df["Volume"].rolling(10).mean().iloc[i]:
                    all_signals.append({
                        "Stock": symbol,
                        "Time": curr["Datetime"],
                        "Close": round(curr["Close"], 2),
                        "Volume": int(curr["Volume"])
                    })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    return pd.DataFrame(all_signals)
