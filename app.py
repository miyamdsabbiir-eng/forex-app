import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
# পৃষ্ঠার কনফিগারেশন
st.set_page_config(
    page_title="Forex & Crypto Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# প্রতি ১০ সেকেন্ডে (10000 মিলিভিসেকেন্ড) পেজ অটো-রিফ্রেশ করার জন্য
st_autorefresh(interval=10000, limit=None, key="trading_dashboard_refresh")

# কাস্টম CSS (আগের ফ্লেক্সবক্স ও কার্ড স্টাইল অক্ষুণ্ণ রেখে)
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
        margin-bottom: 8px;
    }
    .dots-row {
        display: flex;
        gap: 6px; 
        align-items: center;
    }
    .dot-item {
        font-size: 1.3rem;
    }
</style>
""", unsafe_allow_html=True)

# সাইডবার কন্ট্রোল
st.sidebar.markdown("## ⚙️ সেটিংস")
sound_alert_enabled = st.sidebar.toggle("🔊 সাউন্ড অ্যালার্ট", value=True)
st.sidebar.markdown("---")

# টাইমফ্রেমগুলোর তালিকা (১৫মি, ৩০মি, ১ঘ, ২ঘ, ৪ঘ, ১দিন)
timeframes = ["15m", "30m", "1h", "2h", "4h", "1d"]

def analyze_signal(symbol, timeframe):
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
        
        if df.empty or len(df) < 20:
            return "WAIT"
            
        current_price = float(df["Close"].iloc[-1])
        
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty and not pd.isna(rsi_series.iloc[-1]) else 50.0
        
        ema_20 = float(df["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(df["Close'].ewm(span=50, adjust=False).mean().iloc[-1])

        if current_price > ema_50 and ema_20 > ema_50:
            if 40 <= rsi <= 75:
                return "BUY"
            else:
                return "WAIT"
                
        elif current_price < ema_50 and ema_20 < ema_50:
            if 25 <= rsi <= 60:
                return "SELL"
            else:
                return "WAIT"
        else:
            return "WAIT"
            
    except Exception as e:
        return "WAIT"

# হেডার অংশ
st.markdown('<p class="main-header">📊 ফরেক্স ও গোল্ড মার্কেট ওভারভিউ</p>', unsafe_allow_html=True)
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.markdown(f'<p class="sub-caption">🔄 শেষ আপডেট: {current_time} (প্রতি ১০ সেকেন্ডে স্বয়ংক্রিয় আপডেট)</p>', unsafe_allow_html=True)
st.markdown("---")

market_view = st.radio(
    "সিলেক্ট করুন:",
    options=["📈 ফরেক্স ও গোল্ড মার্কেট", "🪙 ক্রিপ্টো ও বিটকয়েন"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")

if market_view == "📈 ফরেক্স ও গোল্ড মার্কেট":
    assets = {
        "Gold (GC/USD)": "GC=F",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
    }
else:
    assets = {
        "Bitcoin (BTC/USD)": "BTC-USD",
        "Ethereum (ETH/USD)": "ETH-USD",
    }

for name, symbol in assets.items():
    with st.container():
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">🏷️ {name}</div>', unsafe_allow_html=True)
        
        dots_html = '<div class="dots-row">'
        for tf_key in timeframes:
            status = analyze_signal(symbol, tf_key)
            
            if status == "BUY":
                dots_html += '<span class="dot-item">🟢</span>'
            elif status == "SELL":
                dots_html += '<span class="dot-item">🔴</span>'
            else:
                dots_html += '<span class="dot-item">🟡</span>'
                
        dots_html += '</div>'
        st.markdown(dots_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
