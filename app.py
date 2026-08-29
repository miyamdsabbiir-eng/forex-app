import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
# পৃষ্ঠার কনফিগারেশন এবং প্রিমিয়াম লুক
st.set_page_config(
    page_title="Smart Money Trading Pro",
    page_icon="⚡",
    layout="wide"
)

# কাস্টম CSS স্টাইল অ্যাপটিকে প্রফেশনাল ও আকর্ষণীয় করার জন্য
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00FFA3;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-caption {
        text-align: center;
        color: #A0AEC0;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    .card {
        background-color: #1E1E2F;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2A2A40;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFFFFF;
    }
    .price-text {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00FFA3;
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

# সাইডবার ডিজাইন
st.sidebar.markdown("## ⚙️ কন্ট্রোল প্যানেল")
st.sidebar.info("📢 **বিজ্ঞাপন শর্ত:**\nঅ্যাপটি সম্পূর্ণ ফ্রি। নিয়ম অনুযায়ী প্রতি **২৪ ঘণ্টায় কমপক্ষে ১টি অ্যাড** দেখতে হবে।")

timeframe_option = st.sidebar.selectbox(
    "📊 টাইমফ্রেম নির্বাচন করুন",
    options=["15m", "1h", "2h", "4h", "1d"],
    index=3
)

sound_alert_enabled = st.sidebar.toggle("🔊 স্পিকার সাوند অ্যালার্ট", value=True)
st.sidebar.markdown("---")
account_balance = st.sidebar.number_input("অ্যাকাউন্ট ব্যালেন্স (USD)", min_value=10.0, value=1000.0, step=50.0)

def get_low_risk_signal(symbol, timeframe):
    try:
        ticker = yf.Ticker(symbol)
        period_map = {"15m": "7d", "1h": "30d", "2h": "60d", "4h": "60d", "1d": "1y"}
        period = period_map.get(timeframe, "60d")
        
        if "BTC" in symbol and timeframe == "15m":
            period = "5d"
            
        df = ticker.history(period=period, interval=timeframe)
        df_daily = ticker.history(period="60d", interval="1d")
        
        if df.empty or df_daily.empty:
            return 0.0, 0.0, 50.0, 0, 0, "ডেটা নেই", 0.0, 0.0, "Error"
            
        current_price = float(df["Close"].iloc[-1])
        previous_close = float(df["Open"].iloc[0])
        percent_change = ((current_price - previous_close) / previous_close) * 100
        
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if not rs.empty else 50.0
        
        ema_20 = float(df["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(df["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
        
        volatility = float(df["Close"].pct_change().std() * current_price)
        if pd.isna(volatility) or volatility == 0:
            volatility = current_price * 0.002

        if current_price > ema_50 and ema_20 > ema_50:
            sm_status, trend_up, trend_down = "বাজার ঊর্ধ্বমুখী (BUY)", 1, 0
            stop_loss = current_price - (volatility * 1.5)
            take_profit = current_price + (volatility * 3.0)
        elif current_price < ema_50 and ema_20 < ema_50:
            sm_status, trend_down, trend_up = "বাজার নিম্নমুখী (SELL)", 1, 0
            stop_loss = current_price + (volatility * 1.5)
            take_profit = current_price - (volatility * 3.0)
            trend_down = 1
            trend_up = 0
        else:
            sm_status, trend_up, trend_down = "অপেক্ষা করুন (WAIT)", 0, 0
            stop_loss, take_profit = 0.0, 0.0
            
        return current_price, percent_change, rsi, trend_up, trend_down, sm_status, stop_loss, take_profit, "Success"
    except Exception as e:
        return 0.0, 0.0, 50.0, 0, 0, "ত্রুটি", 0.0, 0.0, str(e)

# প্রধান শিরোনাম
st.markdown('<p class="main-header">⚡ স্মার্ট মানি ট্রেডিং প্রো</p>', unsafe_allow_html=True)
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.markdown(f'<p class="sub-caption">🔄 রিয়েল-টাইম আপডেট: {current_time} &nbsp;|&nbsp; টাইমফ্রেম: {timeframe_option}</p>', unsafe_allow_html=True)
st.markdown("---")

market_view = st.radio(
    "🌐 মার্কেট মোড পরিবর্তন করুন:",
    options=["📈 ফরেক্স মার্কেট (৫ দিন)", "🪙 ক্রিপ্টো ও বিটকয়েন (৭ দিন)"],
    horizontal=True
)
st.markdown("---")

signal_triggered = False

if market_view == "📈 ফরেক্স মার্কেট (৫ দিন)":
    st.markdown("### 📊 ফরেক্স মার্কেট প্যানেল")
    forex_symbols = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
    }
    
    for name, symbol in forex_symbols.items():
        price, change, rsi, t_up, t_down, sm_status, sl, tp, status = get_low_risk_signal(symbol, timeframe_option)

        if status == "Success":
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1.2, 1.2, 2.0, 2.6])
                
                c1.markdown(f"**{name}**")
                change_color = "normal" if change >= 0 else "inverse"
                c2.metric(label="বর্তমান মূল্য", value=f"{price:.4f}", delta=f"{change:.2f}%")
                c3.text(f"স্ট্যাটাস: {sm_status}\nRSI সূচক: {rsi:.1f}")
                
                if t_up == 1 and 40 <= rsi <= 72:
                    c4.success(f"🟢 **BUY SIGNAL**\nSL: {sl:.4f} | TP: {tp:.4f}")
                    signal_triggered = True
                elif t_down == 1 and 28 <= rsi <= 60:
                    c4.error(f"🔴 **SELL SIGNAL**\nSL: {sl:.4f} | TP: {tp:.4f}")
                    signal_triggered = True
                else:
                    c4.warning("🟡 **WAIT (অপেক্ষা করুন)**")
                st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("### 🪙 ক্রিপ্টো ও বিটকয়েন মার্কেট")
    crypto_symbols = {
        "Bitcoin (BTC/USD)": "BTC-USD",
        "Ethereum (ETH/USD)": "ETH-USD",
    }
    
    for name, symbol in crypto_symbols.items():
        price, change, rsi, t_up, t_down, sm_status, sl, tp, status = get_low_risk_signal(symbol, timeframe_option)

        if status == "Success":
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1.5, 1.3, 2.0, 2.6])
                
                c1.markdown(f"**{name}**")
                c2.metric(label="বর্তমান মূল্য", value=f"${price:,.2f}", delta=f"{change:.2f}%")
                c3.text(f"স্ট্যাটাস: {sm_status}\nRSI সূচক: {rsi:.1f}")
                
                if t_up == 1 and 42 <= rsi <= 78:
                    c4.success(f"🟢 **BUY SIGNAL**\nSL: ${sl:,.2f} | TP: ${tp:,.2f}")
                    signal_triggered = True
                elif t_down == 1 and 22 <= rsi <= 58:
                    c4.error(f"🔴 **SELL SIGNAL**\nSL: ${sl:,.2f} | TP: ${tp:,.2f}")
                    signal_triggered = True
                else:
                    c4.warning("🟡 **WAIT (অপেক্ষা করুন)**")
                st.markdown('</div>', unsafe_allow_html=True)

if signal_triggered and sound_alert_enabled:
    st.markdown('<script>playAlertSound();</script>', unsafe_allow_html=True)
