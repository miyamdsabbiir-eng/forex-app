import pandas as pd
import yfinance as yf

def get_one_line_signals(symbol="BTC-USD"):
    df_5m = yf.download(symbol, interval="5m", period="2d", progress=False)
    df_15m = yf.download(symbol, interval="15m", period="5d", progress=False)
    df_30m = yf.download(symbol, interval="30m", period="5d", progress=False)
    df_1h = yf.download(symbol, interval="1h", period="10d", progress=False)
    df_1d = yf.download(symbol, interval="1d", period="2mo", progress=False)

    for df in [df_5m, df_15m, df_30m, df_1h, df_1d]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    df_10m = df_5m.resample("10min").agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()
    df_2h = df_1h.resample("2h").agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()
    df_4h = df_1h.resample("4h").agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()

    tfs = [df_5m, df_10m, df_15m, df_30m, df_1h, df_2h, df_4h, df_1d]
    signs = []
    
    for df in tfs:
        if df.empty:
            signs.append("🟡")
            continue
        ema = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        close = df['Close'].iloc[-1]
        signs.append("🟢" if close > ema else "🔴")

    return f"{symbol} | " + " ".join(signs)

# st.write(get_one_line_signals("BTC-USD"))
