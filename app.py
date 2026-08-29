import datetime
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="Smart Money Crypto & Forex Dashboard",
    page_icon="🚦",
    layout="wide",
)

st_autorefresh(interval=60000, key="market_signal_refresh")

# ২. কাস্টম ডিজাইন ও স্পিকার সাউন্ড অ্যালার্ট স্ক্রিপ্ট
st.markdown(
    """
    <style>
    .main { background-color: #ffffff; color: #1f1f1f; }
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #e3f2fd; }
    </style>
    
    <script>
    function playAlertSound() {
        var audio = new Audio('https://commondatastorage.googleapis.com/codesign-playground.appspot.com/beep-07.mp3');
        audio.play().catch(function(error) {
            console.log("Audio play blocked: ", error);
        });
    }
    </script>
    """,
    unsafe_allow_html=True,
)

# ৩. সাইডবার কনফিগারেশন
st.sidebar.header("⚙️ সেটিংস ও কন্ট্রোল প্যানেল")

timeframe_option = st.sidebar.selectbox(
    "📊 টাইমফ্রেম সিলেক্ট করুন",
    options=["15m", "1h", "2h", "4h", "1d"],
    index=3
)

sound_alert_enabled = st.sidebar.checkbox("🔊 স্পিকার সাউন্ড অ্যালার্ট চালু রাখুন", value=True)

st.sidebar.markdown("---")
account_balance = st.sidebar.number_input(
    "অ্যাকাউন্ট ব্যালেন্স (USD)", min_value=10.0, value=1000.0, step=50.0
)
risk_percentage = st.sidebar.slider(
    "ঝুঁকি গ্রহণের মাত্রা (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1
)

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 ট্রাফিক লাইট ও স্মার্ট মানি নির্দেশিকা")
st.sidebar.markdown("🟢 **সবুজ লাইট:** স্মার্ট মানি লং (Buy) পজিশনে রয়েছে।")
st.sidebar.markdown("🔴 **লাল লাইট:** স্মার্ট মানি শর্ট (Sell) পজিশনে রয়েছে।")
st.sidebar.markdown("🟡 **হলুদ লাইট:** স্মার্ট মানি কনসোলিডেশনে, এন্ট্রি নিষেধ।")

st.title("🚦 ক্রিপ্টো ও ফরেক্স স্মার্ট মানি ট্রাফিক সিগন্যাল ড্যাশবোর্ড")
st.write(
    f"নির্বাচিত টাইমফ্রেম: **{timeframe_option}** | বিটকয়েনসহ প্রধান পেয়ারগুলোর ইনস্টিটিউশনাল ফ্লো ট্র্যাক করা হচ্ছে।"
)

# ৪. ডেটা ফেচিং এবং স্মার্ট মানি স্ট্রাকচার ফিল্টার ফাংশন
def get_traffic_signal_data(symbol, timeframe):
    try:
        ticker = yf.Ticker(symbol)
        
        period_map = {
            "15m": "7d",
            "1h": "30d",
            "2h": "60d",
            "4h": "60d",
            "1d": "1y"
        }
        period = period_map.get(timeframe, "60d")
        
        df = ticker.history(period=period, interval=timeframe)
        
        if df.empty or len(df) < 50:
            return 0.0, 0.0, 50.0, 0.0, 0, 0, "NEUTRAL", 0.1, "Error"
            
        current_price = float(df["Close"].iloc[-1])
        previous_close = float(df["Open"].iloc[0])
        
        price_change = current_price - previous_close
        percent_change = (price_change / previous_close) * 100
        
        # RSI হিসাব
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1])
        
        # মুভিং এভারেজ (EMA 20, 50, 200)
        ema_20 = float(df["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(df["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
        ema_200 = float(df["Close"].ewm(span=200, adjust=False).mean().iloc[-1])
        
        # স্মার্ট মানি ডিরেকশন ডিটেকশন
        if current_price > ema_50 and ema_20 > ema_50 and ema_50 > ema_200:
            smart_money_status = "BULLISH (BUY)"
            trend_up = 1
            trend_down = 0
        elif current_price < ema_50 and ema_20 < ema_50 and ema_50 < ema_200:
            smart_money_status = "BEARISH (SELL)"
            trend_up = 0
            trend_down = 1
        else:
            smart_money_status = "ACCUMULATION / MANIPULATION (WAIT)"
            trend_up = 0
            trend_down = 0
        
        volatility = float(df["Close"].pct_change().std() * 100)
        if pd.isna(volatility):
            volatility = 0.1
            
        return (
            current_price,
            percent_change,
            current_rsi,
            ema_50,
            trend_up,
            trend_down,
            smart_money_status,
            volatility,
            "Success",
        )
    except Exception as e:
        return 0.0, 0.0, 50.0, 0.0, 0, 0, "ERROR", 0.1, str(e)

# ৫. পেয়ার ও ক্রিপ্টোর তালিকা (এখানে বিটকয়েন যুক্ত করা হয়েছে)
symbols = {
    "Bitcoin (BTC/USD)": "BTC-USD",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
}

st.subheader(f"📊 লাইভ স্মার্ট মানি ট্র্যাকিং প্যানেল ({timeframe_option})")

current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.caption(f"🔄 সর্বশেষ আপডেট: {current_time} (প্রতি ৬০ সেকেন্ডে অটো-চেক)")

for name, symbol in symbols.items():
    (
        price,
        change,
        rsi,
        ema,
        trend_up,
        trend_down,
        smart_money,
        volatility,
        status,
    ) = get_traffic_signal_data(symbol, timeframe_option)

    if status == "Success":
        base_lot = (account_balance / 1000) * 0.1
        if volatility < 0.05:
            dynamic_lot = round(max(0.01, base_lot * 1.5), 2)
        elif volatility > 0.15:
            dynamic_lot = 0.01
        else:
            dynamic_lot = round(max(0.01, base_lot), 2)

        if dynamic_lot > 0.3:
            dynamic_lot = 0.3

        col1, col2, col3 = st.columns([2, 2, 3])

        with col1:
            st.metric(
                label=name,
                value=f"{price:,.2f}" if "BTC" in name else f"{price:.4f}",
                delta=f"{change:.2f}%",
            )

        with col2:
            st.metric(
                label=f"স্মার্ট মানি স্ট্যাটাস",
                value=f"{smart_money}",
                delta=f"RSI: {rsi:.1f}",
            )

        with col3:
            if trend_up == 1 and rsi >= 45 and rsi <= 70:
                st.success(f"🟢 সংকেত: BUY (স্মার্ট মানির অনুকূলে লং)")
                st.info(f"💡 প্রস্তাবিত লট: {dynamic_lot} Lots")
                
                if sound_alert_enabled:
                    st.markdown('<script>playAlertSound();</script>', unsafe_allow_html=True)
                    
            elif trend_down == 1 and rsi <= 55 and rsi >= 30:
                st.error(f"🔴 সংকেত: SELL (স্মার্ট মানির অনুকূলে শর্ট)")
                st.info(f"💡 প্রস্তাবিত লট: {dynamic_lot} Lots")
                
                if sound_alert_enabled:
                    st.markdown('<script>playAlertSound();</script>', unsafe_allow_html=True)
                    
            else:
                st.warning("🟡 সংকেত: WAIT (ফেক জোন / ম্যানিপুলেশন চলছে)")
                st.info("💡 স্মার্ট মানি কনফার্মেশন না পাওয়া পর্যন্ত অপেক্ষা করুন")
    else:
        st.error(f"{name} এর ডেটা আনতে সমস্যা হচ্ছে।")

    st.markdown("---")
