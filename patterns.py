# kotegawa_screener/patterns.py

def is_bullish_engulfing(prev, curr):
    return (
        float(prev["Close"]) < float(prev["Open"]) and
        float(curr["Close"]) > float(curr["Open"]) and
        float(curr["Open"]) < float(prev["Close"]) and
        float(curr["Close"]) > float(prev["Open"])
    )

def is_hammer(candle):
    open_price = float(candle["Open"])
    close_price = float(candle["Close"])
    low = float(candle["Low"])
    high = float(candle["High"])

    body = abs(close_price - open_price)
    lower_wick = min(open_price, close_price) - low
    upper_wick = high - max(open_price, close_price)

    return lower_wick > 2 * body and upper_wick < body
