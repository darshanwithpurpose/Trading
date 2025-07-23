# kotegawa_screener/backtest_eod.py

import yfinance as yf
import pandas as pd

def backtest_kotegawa_daily(symbol, start="2020-01-01", end="2023-12-31", mode="5d"):
    try:
        ticker = symbol if ".NS" in symbol else symbol + ".NS"
        df = yf.download(ticker, start=start, end=end, progress=False)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        trades = []

        if mode == "5d":
            for i in range(5, len(df) - 1):
                last5 = df.iloc[i - 5:i]
                day = df.iloc[i]

                highest_high = last5['High'].max()
                lowest_low = last5['Low'].min()
                avg_vol = last5['Volume'].mean()

                if day['Close'] > highest_high and day['Volume'] > avg_vol:
                    entry = day['Close']
                    sl = lowest_low
                    target = entry + (entry - sl) * 1.5

                    outcome = "OPEN"
                    exit_price = None

                    for j in range(i + 1, min(i + 10, len(df))):
                        if df['Low'].iloc[j] <= sl:
                            outcome = "HIT_SL"
                            exit_price = sl
                            break
                        if df['High'].iloc[j] >= target:
                            outcome = "HIT_TARGET"
                            exit_price = target
                            break

                    trades.append({
                        'Date': day['Date'],
                        'Entry': round(entry, 2),
                        'SL': round(sl, 2),
                        'Target': round(target, 2),
                        'ExitPrice': round(exit_price, 2) if exit_price else None,
                        'Outcome': outcome
                    })

        return pd.DataFrame(trades)
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])
