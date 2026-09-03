import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
# পৃষ্ঠার কনফিগারেশন
st.set_page_config(
    page_title="Smart Money Trading Pro",
    page_icon="⚡",
    layout="wide"
)

# কাস্টম CSS স্টাইল (ডটগুলোকে অক্ষরের মতো একদম কাছাকাছি রাখার জন্য)
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #00FFA3;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-caption {
        text-align: center;
        color: #A0AEC0;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    .card {
        background-color: #1E1E2F;
        padding: 12px 15px;
        border-radius: 10px;
        border: 1px solid #2A2A40;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .dots-row {
        display: flex;
        gap: 6px; /* অক্ষরের মতো একদম কাছাকাছি রাখার জন্য গ্যাপ কমানো হয়েছে */
        align-items: center;
        margin-top: 8px;
    }
    .dot-item {
        font-size: 1.4rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
function playAlertSound() {
    var audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
    audio.play();
}
</script>
""", unsafe_allow_html=True)

# সাইডবার
st.sidebar.markdown("## ⚙️ কন্ট্রোল প্যানেল")
sound_alert_enabled = st.sidebar.toggle("🔊 স্পিকার সাউন্ড অ্যালার্ট", value=True)
st.sidebar.markdown("---")
account_balance = st.sidebar.number_input("অ্যাকাউন্ট ব্যালেন্স (USD)", min_value=10.0, value=1000.0, step=50.0)

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
            return "WAIT", 0.0, 50.0, 0.0, 0.0
            
        current_price = float(df["Close"].iloc[-1])
        
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty and not pd.isna(rsi_series.iloc[-1]) else 50.0
        
        ema_20 = float(df["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(df["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
        
        volatility = float(df["Close"].pct_change().std() * current_price)
        if pd.isna(volatility) or volatility == 0:
            volatility = current_price * 0.002

        if current_price > ema_50 and ema_20 > ema_50:
            if 40 <= rsi <= 75:
                stop_loss = current_price - (volatility * 1.5)
                take_profit = current_price + (volatility * 3.0)
                return "BUY", current_price, rsi, stop_loss, take_profit
            else:
                return "WAIT", current_price, rsi, 0.0, 0.0
                
        elif current_price < ema_50 and ema_20 < ema_50:
            if 25 <= rsi <= 60:
                stop_loss = current_price + (volatility * 1.5)
                take_profit = current_price - (volatility * 3.0)
                return "SELL", current_price, rsi, stop_loss, take_profit
            else:
                return "WAIT", current_price, rsi, 0.0, 0.0
        else:
            return "WAIT", current_price, rsi, 0.0, 0.0
            
    except Exception as e:
        return "WAIT", 0.0, 50.0, 0.0, 0.0

# হেডার
st.markdown('<p class="main-header">⚡ স্মার্ট মানি ট্রেডিং প্রো</p>', unsafe_allow_html=True)
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.markdown(f'<p class="sub-caption">🔄 লাইভ আপডেট (Ultra-Tight Mode): {current_time}</p>', unsafe_allow_html=True)
st.markdown("---")

market_view = st.radio(
    "🌐 মার্কেট মোড পরিবর্তন করুন:",
    options=["📈 ফরেক্স ও গোল্ড মার্কেট", "🪙 ক্রিপ্টো ও বিটকয়েন"],
    horizontal=True
)
st.markdown("---")

signal_triggered = False

if market_view == "📈 ফরেক্স ও গোল্ড মার্কেট":
    st.markdown("### 📊 ফরেক্স ও গোল্ড মার্কেট ওভারভিউ")
    assets = {
        "Gold (GC/USD)": "GC=F",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
    }
else:
    st.markdown("### 🪙 ক্রিপ্টো মার্কেট ওভারভিউ")
    assets = {
        "Bitcoin (BTC/USD)": "BTC-USD",
        "Ethereum (ETH/USD)": "ETH-USD",
    }

for name, symbol in assets.items():
    with st.container():
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f"##### 🏷️ {name}")
        
        dots_html = '<div class="dots-row">'
        for tf_key in timeframes:
            status, price, rsi, sl, tp = analyze_signal(symbol, tf_key)
            
            if status == "BUY":
                dots_html += '<span class="dot-item">🟢</span>'
                signal_triggered = True
            elif status == "SELL":
                dots_html += '<span class="dot-item">🔴</span>'
                signal_triggered = True
            else:
                dots_html += '<span class="dot-item">🟡</span>'
                
        dots_html += '</div>'
        st.markdown(dots_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if signal_triggered and sound_alert_enabled:
    st.markdown('<script>playAlertSound();</script>', unsafe_allow_html=True)
