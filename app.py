import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from streamlit_autorefresh import st_autorefresh

# পৃষ্ঠার কনফিগারেশন
st.set_page_config(
    page_title="Ultra-Secure Smart Trading Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# অটো-রিফ্রেশ সময় ৫ মিনিট (৩০০০০০ মিলিভিসেকেন্ড)
st_autorefresh(interval=300000, limit=None, key="safe_dashboard_refresh")

# কাস্টম CSS ডিজাইন (প্রফেশনাল ডার্ক থিম)
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0px;
    }
    .sub-caption {
        color: #8E9297;
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
    .card {
        background-color: #121212;
        padding: 14px 18px;
        border-radius: 8px;
        border: 1px solid #2A2A2A;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 10px;
    }
    .signals-row {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        align-items: center;
    }
    .signal-item {
        display: flex;
        align-items: center;
        gap: 5px;
        background-color: #1E1E1E;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #C5C6C7;
    }
</style>
""", unsafe_allow_html=True)

timeframes = ["15m", "30m", "1h", "2h", "4h", "1d"]

def analyze_ultra_safe_signal(symbol, timeframe):
    try:
        ticker = yf.Ticker(symbol)
        period_map = {
            "15m": "5d", 
            "30m": "7d",
            "1h": "30d", 
            "2h": "60d", 
            "4h": "60d", 
            "1d": "1y"
        }
        period = period_map.get(timeframe, "60d")
        df = ticker.history(period=period, interval=timeframe)
        
        if df.empty or len(df) < 50:
            return "WAIT"
            
        current_price = float(df["Close"].iloc[-1])
        
        # ১. EMA (20 & 50) - ট্রেন্ড ফিল্টার
        ema_20 = df["Close"].ewm(span=20, adjust=False).mean()
        ema_50 = df["Close"].ewm(span=50, adjust=False).mean()
        
        # ২. RSI (14) - মোমেন্টাম জোন
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # ৩. MACD - ট্রেন্ড কনফার্মেশন
        exp1 = df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = df["Close"].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        
        # ৪. OBV (স্মার্ট মানি ভলিউম ফ্লো)
        obv = (np.sign(df["Close"].diff()) * df["Volume"]).fillna(0).cumsum()
        obv_ema = obv.ewm(span=20, adjust=False).mean()

        curr_rsi = float(rsi.iloc[-1])
        curr_macd = float(macd.iloc[-1])
        curr_signal = float(signal_line.iloc[-1])
        curr_ema20 = float(ema_20.iloc[-1])
        curr_ema50 = float(ema_50.iloc[-1])
        curr_obv = float(obv.iloc[-1])
        curr_obv_ema = float(obv_ema.iloc[-1])

        # লস এড়াতে অত্যন্ত কঠোর কনফ্লুয়েন্স লজিক (সব শর্ত একসাথে মিললেই কেবল সিগন্যাল দেবে)
        if current_price > curr_ema50 and curr_ema20 > curr_ema50:
            # অতিরিক্ত ওভারবট জোন এড়ানোর জন্য RSI < 65 রাখা হয়েছে যাতে পিক পয়েন্টে ফাসতে না হয়
            if 50 <= curr_rsi <= 65 and curr_macd > curr_signal and curr_obv > curr_obv_ema:
                return "BUY"
            else:
                return "WAIT"
                
        elif current_price < curr_ema50 and curr_ema20 < curr_ema50:
            # অতিরিক্ত ওভারসোল্ড জোন এড়ানোর জন্য RSI > 35 রাখা হয়েছে
            if 35 <= curr_rsi <= 50 and curr_macd < curr_signal and curr_obv < curr_obv_ema:
                return "SELL"
            else:
                return "WAIT"
        else:
            return "WAIT"
            
    except Exception as e:
        return "WAIT"

st.markdown('<p class="main-header">🛡️ প্রোটেক্টেড স্মার্ট মানি ট্রেডিং ড্যাশবোর্ড</p>', unsafe_allow_html=True)
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.markdown(f'<p class="sub-caption">🔄 শেষ আপডেট: {current_time} (লস প্রটেকশন ফিল্টার সক্রিয়)</p>', unsafe_allow_html=True)
st.markdown("---")

market_view = st.radio(
    "সিলেক্ট করুন:",
    options=["📈 ফরেক্স ও কমোডিটিস", "🪙 ক্রিপ্টোকারেন্সি"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")

if market_view == "📈 ফরেক্স ও কমোডিটিস":
    assets = {
        "Gold (GC/USD)": "GC=F",
        "Silver (SI/USD)": "SI=F",
        "Crude Oil": "CL=F",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X"
    }
else:
    assets = {
        "Bitcoin (BTC/USD)": "BTC-USD",
        "Ethereum (ETH/USD)": "ETH-USD",
        "Binance Coin (BNB/USD)": "BNB-USD",
        "Solana (SOL/USD)": "SOL-USD",
        "Ripple (XRP/USD)": "XRP-USD",
        "Cardano (ADA/USD)": "ADA-USD"
    }

for name, symbol in assets.items():
    with st.container():
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">🏷️ {name}</div>', unsafe_allow_html=True)
        
        signals_html = '<div class="signals-row">'
        for tf_key in timeframes:
            status = analyze_ultra_safe_signal(symbol, tf_key)
            
            if status == "BUY":
                dot = "🟢"
            elif status == "SELL":
                dot = "🔴"
            else:
                dot = "🟡"
                
            signals_html += f'<div class="signal-item"><b>{tf_key}</b>: {dot}</div>'
                
        signals_html += '</div>'
        st.markdown(signals_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
