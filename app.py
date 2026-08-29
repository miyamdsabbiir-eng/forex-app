import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
# ১. পেজ কনফিগারেশন (কমপ্যাক্ট লেআউট)
st.set_page_config(
    page_title="Smart Money Low-Risk Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ২. সাউন্ড অ্যালার্টের জাভাস্ক্রিপ্ট
st.markdown("""
<script>
function playAlertSound() {
    var audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
    audio.play();
}
</script>
""", unsafe_allow_html=True)

# ৩. সাইডবার কন্ট্রোল প্যানেল
st.sidebar.header("⚙️ কন্ট্রোল প্যানেল")

timeframe_option = st.sidebar.selectbox(
    "📊 টাইমফ্রেম",
    options=["15m", "1h", "2h", "4h", "1d"],
    index=3
)

sound_alert_enabled = st.sidebar.toggle("🔊 স্পিকার সাউন্ড অ্যালার্ট", value=True)

st.sidebar.markdown("---")
account_balance = st.sidebar.number_input("ব্যালেন্স (USD)", min_value=10.0, value=1000.0, step=50.0)

# ৪. অ্যাডভান্সড লস-প্রিভেনশন ডেটা ফেচিং ফাংশন
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
            return 0.0, 0.0, 50.0, 0, 0, "NO DATA", 0.0, 0.0, "Error"
            
        current_price = float(df["Close"].iloc[-1])
        previous_close = float(df["Open"].iloc[0])
        percent_change = ((current_price - previous_close) / previous_close) * 100
        
        # RSI হিসাব
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if not rs.empty else 50.0
        
        # মুভিং এভারেজ
        ema_20 = float(df["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(df["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
        daily_ema_50 = float(df_daily["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
        
        volatility = float(df["Close"].pct_change().std() * current_price)
        if pd.isna(volatility) or volatility == 0:
            volatility = current_price * 0.002

        if current_price > ema_50 and ema_20 > ema_50 and current_price > daily_ema_50:
            sm_status, trend_up, trend_down = "BULLISH (STRONG)", 1, 0
            stop_loss = current_price - (volatility * 1.5)
            take_profit = current_price + (volatility * 3.0)
        elif current_price < ema_50 and ema_20 < ema_50 and current_price < daily_ema_50:
            sm_status, trend_up, trend_down = "BEARISH (STRONG)", 0, 1
            stop_loss = current_price + (volatility * 1.5)
            take_profit = current_price - (volatility * 3.0)
        else:
            sm_status, trend_up, trend_down = "CHOPPY / WAIT", 0, 0
            stop_loss, take_profit = 0.0, 0.0
            
        return current_price, percent_change, rsi, trend_up, trend_down, sm_status, stop_loss, take_profit, "Success"
    except Exception as e:
        return 0.0, 0.0, 50.0, 0, 0, "ERROR", 0.0, 0.0, str(e)

# ৫. মূল ইন্টারফেস ও ওপরে মার্কেট সিলেকশন সুইচ (Radio Buttons with horizontal layout)
st.title("🛡️ Smart Money Low-Risk Dashboard")
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.caption(f"🔄 আপডেট: {current_time} | টাইমফ্রেম: {timeframe_option}")
st.markdown("---")

market_view = st.radio(
    "🌐 মার্কেট সুইচ:",
    options=["📈 ফরেক্স মার্কেট (৫ দিন)", "🪙 ক্রিপ্টো ও বিটকয়েন (৭ দিন)"],
    horizontal=True
)
st.markdown("---")

signal_triggered = False

# মার্কেট সিলেকশন অনুযায়ী ডিসপ্লে
if market_view == "📈 ফরেক্স মার্কেট (৫ দিন)":
    st.subheader("📊 ফরেক্স মার্কেট ট্র্যাকিং প্যানেল")
    forex_symbols = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
    }
    
    col_h1, col_h2, col_h3, col_h4 = st.columns([1.2, 1.2, 2.2, 2.4])
    col_h1.markdown("**పేয়ার**")
    col_h2.markdown("**প্রাইস**")
    col_h3.markdown("**স্মার্ট মানি ট্রেন্ড**")
    col_h4.markdown("**সুরক্ষিত সিগন্যাল ও SL/TP**")
    st.markdown("---")

    for name, symbol in forex_symbols.items():
        price, change, rsi, t_up, t_down, sm_status, sl, tp, status = get_low_risk_signal(symbol, timeframe_option)

        if status == "Success":
            c1, c2, c3, c4 = st.columns([1.2, 1.2, 2.2, 2.4])
            c1.write(f"**{name}**")
            c2.text(f"{price:.4f}")
            c3.text(f"{sm_status}\n(RSI: {rsi:.1f})")
            
            if t_up == 1 and 48 <= rsi <= 65:
                c4.success(f"🟢 BUY\nSL: {sl:.4f} | TP: {tp:.4f}")
                signal_triggered = True
            elif t_down == 1 and 35 <= rsi <= 52:
                c4.error(f"🔴 SELL\nSL: {sl:.4f} | TP: {tp:.4f}")
                signal_triggered = True
            else:
                c4.warning("🟡 WAIT")
        else:
            st.error(f"{name}: ডেটা লোড হয়নি")

else:
    st.subheader("🪙 ক্রিপ্টো ও বিটকয়েন মার্কেট (৭ দিন)")
    crypto_symbols = {
        "Bitcoin (BTC/USD)": "BTC-USD",
        "Ethereum (ETH/USD)": "ETH-USD",
    }
    
    col_h1, col_h2, col_h3, col_h4 = st.columns([1.5, 1.3, 2.2, 2.5])
    col_h1.markdown("**কয়েন**")
    col_h2.markdown("**প্রাইস**")
    col_h3.markdown("**স্মার্ট মানি ট্রেন্ড**")
    col_h4.markdown("**সুরক্ষিত সিগন্যাল ও SL/TP**")
    st.markdown("---")

    for name, symbol in crypto_symbols.items():
        price, change, rsi, t_up, t_down, sm_status, sl, tp, status = get_low_risk_signal(symbol, timeframe_option)

        if status == "Success":
            c1, c2, c3, c4 = st.columns([1.5, 1.3, 2.2, 2.5])
            c1.write(f"**{name}**")
            c2.text(f"${price:,.2f}")
            c3.text(f"{sm_status}\n(RSI: {rsi:.1f})")
            
            if t_up == 1 and 48 <= rsi <= 65:
                c4.success(f"🟢 BUY\nSL: ${sl:,.2f} | TP: ${tp:,.2f}")
                signal_triggered = True
            elif t_down == 1 and 35 <= rsi <= 52:
                c4.error(f"🔴 SELL\nSL: ${sl:,.2f} | TP: ${tp:,.2f}")
                signal_triggered = True
            else:
                c4.warning("🟡 WAIT")
        else:
            st.error(f"{name}: ডেটা লোড হয়নি")

# সাউন্ড ট্রিগার
if signal_triggered and sound_alert_enabled:
    st.markdown('<script>playAlertSound();</script>', unsafe_allow_html=True)
