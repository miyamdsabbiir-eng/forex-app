import pandas as pd
import streamlit as st
import yfinance as yf

def get_one_line_signals(symbol="BTC-USD"):
    # বিভিন্ন টাইমফ্রেমের ডেটা ফেচ করা
    df_5m = yf.download(symbol, interval="5m", period="2d", progress=False)
    df_15m = yf.download(symbol, interval="15m", period="5d", progress=False)
    df_30m = yf.download(symbol, interval="30m", period="5d", progress=False)
    df_1h = yf.download(symbol, interval="1h", period="10d", progress=False)
    df_1d = yf.download(symbol, interval="1d", period="2mo", progress=False)

    # মাল্টি-ইনডেক্স কলাম সমস্যা সমাধান
    for df in [df_5m, df_15m, df_30m, df_1h, df_1d]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    # রিসেম্পল করে ১০ মিনিট, ২ ঘণ্টা এবং ৪ ঘণ্টার ডেটা তৈরি করা
    df_10m = df_5m.resample("10min").agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna() if not df_5m.empty else pd.DataFrame()
    df_2h = df_1h.resample("2h").agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna() if not df_1h.empty else pd.DataFrame()
    df_4h = df_1h.resample("4h").agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna() if not df_1h.empty else pd.DataFrame()

    for df in [df_10m, df_2h, df_4h]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    # ৮টি টাইমফ্রেমের সিকোয়েন্স সাজানো
    tfs = [df_5m, df_10m, df_15m, df_30m, df_1h, df_2h, df_4h, df_1d]
    signs = []
    
    # EMA (20) এর সাপেক্ষে সিগন্যাল জেনারেট করা
    for df in tfs:
        if df.empty or len(df) < 20:
            signs.append("🟡")
            continue
        ema = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        close = df['Close'].iloc[-1]
        signs.append("🟢" if close > ema else "🔴")

    return f"{symbol}  |  " + "  ".join(signs)

# স্ট্রিমলিট ড্যাশবোর্ড ইন্টারফেস
st.subheader("Multi-Timeframe Trend Dashboard (Crypto & Forex)")
st.markdown("টাইমফ্রেম সিকোয়েন্স: **5m | 10m | 15m | 30m | 1h | 2h | 4h | 1d**")
st.markdown("---")

# ক্রিপ্টো এবং ফরেক্স পেয়ারগুলোর তালিকা
symbols = [
    # ক্রিপ্টোকারেন্সি
    "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",
    # ফরেক্স পেয়ার (4x)
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"
]

for sym in symbols:
    signal_line = get_one_line_signals(sym)
    st.markdown(f"### `{signal_line}`")
