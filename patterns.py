# kotegawa_screener/patterns.py

def is_bullish_engulfing(prev, curr):
    return prev['Close'] < prev['Open'] and \
           curr['Close'] > curr['Open'] and \
           curr['Close'] > prev['Open'] and \
           curr['Open'] < prev['Close']

def is_hammer(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_wick = candle['Open'] - candle['Low'] if candle['Open'] > candle['Close'] else candle['Close'] - candle['Low']
    upper_wick = candle['High'] - max(candle['Close'], candle['Open'])
    return lower_wick > 2 * body and upper_wick < body

def near_support(curr_candle, df):
    recent_lows = df['Low'].rolling(window=10).min()
    return abs(curr_candle['Low'] - recent_lows.iloc[-1]) / curr_candle['Low'] < 0.01
