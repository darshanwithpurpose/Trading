import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Load NIFTY 50 symbols (manual list since yfinance doesn't have a direct call)
nifty_50_symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "LT.NS", "SBIN.NS", "ITC.NS", "KOTAKBANK.NS",
    "BHARTIARTL.NS", "ASIANPAINT.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "AXISBANK.NS", "HCLTECH.NS", "WIPRO.NS",
    "MARUTI.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "SUNPHARMA.NS", "TITAN.NS", "POWERGRID.NS", "ONGC.NS", "ADANIENT.NS",
    "COALINDIA.NS", "TECHM.NS", "NTPC.NS", "JSWSTEEL.NS", "GRASIM.NS", "BAJAJFINSV.NS", "HINDALCO.NS", "BRITANNIA.NS",
    "CIPLA.NS", "BPCL.NS", "EICHERMOT.NS", "HDFCLIFE.NS", "DRREDDY.NS", "DIVISLAB.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS",
    "INDUSINDBK.NS", "SBILIFE.NS", "UPL.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "M&M.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS",
    "SHREECEM.NS"
]

# Backtesting range
end_date = datetime.today()
start_date = end_date - timedelta(days=3*365)

# Pattern detection functions
def is_hammer(candle):
    body = abs(candle['Close'] - candle['Open'])
    lower_shadow = candle['Open'] - candle['Low'] if candle['Close'] > candle['Open'] else candle['Close'] - candle['Low']
    upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
    return lower_shadow > 2 * body and upper_shadow < 0.3 * body

def is_doji(candle):
    return abs(candle['Open'] - candle['Close']) <= (0.1 * (candle['High'] - candle['Low']))

def is_inverted_hammer(candle):
    body = abs(candle['Close'] - candle['Open'])
    upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
    lower_shadow = min(candle['Close'], candle['Open']) - candle['Low']
    return upper_shadow > 2 * body and lower_shadow < 0.3 * body

def find_swing_low(df, i):
    return df['Low'][i] < df['Low'][i - 2] and df['Low'][i] < df['Low'][i - 1] and df['Low'][i] < df['Low'][i + 1] and df['Low'][i] < df['Low'][i + 2]

def find_swing_high(df, i):
    return df['High'][i] > df['High'][i - 2] and df['High'][i] > df['High'][i - 1] and df['High'][i] > df['High'][i + 1] and df['High'][i] > df['High'][i + 2]

# Backtesting engine
def backtest_stock(symbol):
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        df_signals = []

        for i in range(2, len(df) - 2):
            candle = df.iloc[i]
            next_candle = df.iloc[i + 1]

            if find_swing_low(df, i):
                if is_hammer(candle) and next_candle['Close'] > candle['Close']:
                    df_signals.append({'Date': candle['Date'], 'Type': 'Buy', 'Entry': next_candle['Close'],
                                       'Exit': df.iloc[i + 5]['Close'] if i + 5 < len(df) else next_candle['Close']})
                elif is_doji(candle) and next_candle['Close'] > candle['Close']:
                    df_signals.append({'Date': candle['Date'], 'Type': 'Buy', 'Entry': next_candle['Close'],
                                       'Exit': df.iloc[i + 5]['Close'] if i + 5 < len(df) else next_candle['Close']})
                elif is_inverted_hammer(candle) and next_candle['Close'] > candle['Close']:
                    df_signals.append({'Date': candle['Date'], 'Type': 'Buy', 'Entry': next_candle['Close'],
                                       'Exit': df.iloc[i + 5]['Close'] if i + 5 < len(df) else next_candle['Close']})

        if not df_signals:
            return None

        signals_df = pd.DataFrame(df_signals)
        signals_df['Return'] = (signals_df['Exit'] - signals_df['Entry']) / signals_df['Entry']
        total_trades = len(signals_df)
        profitable_trades = len(signals_df[signals_df['Return'] > 0])
        avg_return = signals_df['Return'].mean()

        return {
            'Symbol': symbol,
            'Trades': total_trades,
            'Profitable': profitable_trades,
            'Win %': round(100 * profitable_trades / total_trades, 2),
            'Avg Return %': round(100 * avg_return, 2)
        }
    except Exception:
        return None

# Run backtest on NIFTY 50
results = []
for symbol in nifty_50_symbols:
    result = backtest_stock(symbol)
    if result:
        results.append(result)

results_df = pd.DataFrame(results).sort_values(by="Win %", ascending=False).reset_index(drop=True)
results_df.head()
