# kotegawa_screener/backtest_eod.py

import yfinance as yf
import pandas as pd

def is_bullish_engulfing(prev, curr):
    return (
        prev['Close'] < prev['Open'] and
        curr['Close'] > curr['Open'] and
        curr['Close'] > prev['Open'] and
        curr['Open'] < prev['Close']
    )

def is_hammer(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_wick = min(candle['Open'], candle['Close']) - candle['Low']
    upper_wick = candle['High'] - max(candle['Open'], candle['Close'])
    return lower_wick > 2 * body and upper_wick < body

def near_support(idx, df, window=10):
    if idx < window:
        return False
    recent_low = df['Low'].iloc[idx - window:idx].min()
    return abs(df['Low'].iloc[idx] - recent_low) / df['Low'].iloc[idx] < 0.01

def backtest_kotegawa_daily(symbol, start="2020-01-01", end="2023-12-31"):
    try:
        ticker = symbol if ".NS" in symbol else symbol + ".NS"
        df = yf.download(ticker, start=start, end=end, progress=False)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        trades = []

        for i in range(1, len(df) - 1):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]

            if (is_bullish_engulfing(prev, curr) or is_hammer(curr)) and \
               curr['Volume'] > df['Volume'].rolling(10).mean().iloc[i] and \
               near_support(i, df):

                entry = curr['High'] + 0.1
                sl = curr['Low']
                target = entry + (entry - sl) * 1.5

                outcome = "OPEN"
                for j in range(i + 1, min(i + 10, len(df))):
                    if df['Low'].iloc[j] <= sl:
                        outcome = "HIT_SL"
                        break
                    if df['High'].iloc[j] >= target:
                        outcome = "HIT_TARGET"
                        break

                trades.append({
                    'Date': curr['Date'],
                    'Entry': round(entry, 2),
                    'SL': round(sl, 2),
                    'Target': round(target, 2),
                    'Outcome': outcome
                })

        return pd.DataFrame(trades)
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])
