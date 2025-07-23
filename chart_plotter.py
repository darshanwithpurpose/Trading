# kotegawa_screener/utils/chart_plotter.py

import yfinance as yf
import mplfinance as mpf

def plot_chart_with_signals(symbol, tf="5m"):
    ticker = symbol if ".NS" in symbol else symbol + ".NS"
    df = yf.download(ticker, period="1d", interval=tf, progress=False)
    df.index.name = "Date"
    mpf.plot(df, type="candle", volume=True, title=f"{symbol} ({tf})")
