# kotegawa_screener/utils/chart_plotter.py

import yfinance as yf
import mplfinance as mpf

def plot_chart_with_signals(symbol, tf):
    tf_map = {"5m": "5m", "15m": "15m"}
    if symbol in ["NIFTY", "BANKNIFTY"]:
        ticker = "^NSEI" if symbol == "NIFTY" else "^NSEBANK"
    else:
        ticker = symbol + ".NS"

    df = yf.download(ticker, period="1d", interval=tf_map[tf], progress=False)
    df.index.name = 'Date'

    mpf.plot(df, type='candle', style='charles', volume=True, title=f"{symbol} Intraday Chart")
