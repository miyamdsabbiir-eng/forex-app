import datetime
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ১. পেজ কনফিগারেশন
st.set_page_config(
    page_title="Forex Traffic Light Signal Dashboard",
    page_icon="🚦",
    layout="wide",
)

st_autorefresh(interval=60000, key="market_signal_refresh")

# ২. কাস্টম রঙিন ডিজাইন ও স্টাইল (CSS)
st.markdown(
    """
    <style>
    .main { background-color: #ffffff; color: #1f1f1f; }
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #e3f2fd; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ৩. সাইডবার কনফিগারেশন
st.sidebar.header("⚙️ সেটিংস ও অ্যাকাউন্ট")
account_balance = st.sidebar.number_input(
    "অ্যাকাউন্ট ব্যালেন্স (USD)", min_value=10.0, value=1000.0, step=50.0
)
risk_percentage = st.sidebar.slider(
    "ঝুঁকি গ্রহণের মাত্রা (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔊 সাউন্ড কন্ট্রোল")
# স্পিকার অন/অফ করার টিক বক্স (Checkbox)
sound_enabled = st.sidebar.checkbox("🔊 স্পিকার অ্যালার্ট অন রাখুন", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 ট্রাফিক লাইট সংকেত নির্দেশিকা")
st.sidebar.markdown(
    "🟢 **সবুজ লাইট (বাই):** ট্রেন্ড ঊর্ধ্বমুখী, লং পজিশন নেওয়ার উপযুক্ত সময়।"
)
st.sidebar.markdown(
    "🔴 **লাল লাইট (সেল):** ট্রেন্ড নিম্নমুখী, শর্ট পজিশন নেওয়ার সময়।"
)
st.sidebar.markdown(
    "🟡 **হলুদ লাইট (অপেক্ষা করুন):** মার্কেট সাইডওয়েজ বা অস্থির, নিরাপদ দূরত্বে থাকুন।"
)

st.title("🚦 ফরেক্স ট্রাফিক লাইট সিগন্যাল ড্যাশবোর্ড")
st.write(
    "রং দেখে সিদ্ধান্ত নিন: সবুজ = বাই, লাল = সেল, হলুদ = নিরাপদ দূরত্বে থাকুন।"
)

# ৮. ডেটা ফেচিং ও ফিল্টার ফাংশন
def get_traffic_signal_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty or len(df) < 14:
            return 0.0, 0.0, 50.0, 0.0, 0, 0.1, "Error"
            
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
        
        # EMA হিসাব
        ema_20 = float(df["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
        
        # ট্রেন্ড এবং ভোলাটিলিটি
        recent_trend = int(df["Close"].iloc[-1] > df["Close"].iloc[-3])
        volatility = float(df["Close"].pct_change().std() * 100)
        if pd.isna(volatility):
            volatility = 0.1
            
        return (
            current_price,
            percent_change,
            current_rsi,
            ema_20,
            recent_trend,
            volatility,
            "Success",
        )
    except Exception as e:
        return 0.0, 0.0, 50.0, 0.0, 0, 0.1, str(e)

# ৫. পেয়ারের তালিকা
symbols = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
}

st.subheader("📊 লাইভ মার্কেট ট্রাফিক সিগন্যাল প্যানেল")

# অটো রিফ্রেশ লজিক
current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
st.caption(f"🔄 সর্বশেষ আপডেট: {current_time} (প্রতি ৬০ সেকেন্ডে অটো-আপডেট)")

for name, symbol in symbols.items():
    (
        price,
        change,
        rsi,
        ema,
        trend,
        volatility,
        status,
    ) = get_traffic_signal_data(symbol)

    if status == "Success":
        # ডাইনামিক লট সাইজ হিসাব
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
                value=f"{price:.4f}",
                delta=f"{change:.2f}%",
            )

        with col2:
            st.metric(
                label="টেকনিক্যাল অবস্থা",
                value=f"RSI: {rsi:.1f}",
                delta=f"EMA: {ema:.4f}",
            )

        with col3:
            # ট্রাফিক লাইট লজিক
            if rsi < 38 and price >= ema and trend >= 0:
                st.success("🟢 সংকেত: BUY (বাজেট ঝুঁকি অনুযায়ী লং করুন)")
                st.info(f"💡 প্রস্তাবিত লট সাইজ: {dynamic_lot} Lots")
                
                # যদি স্পিকার অন থাকে, তবে ব্রাউজারে বীপ সাউন্ড বাজানোর ছোট্ট এইচটিএমএল কোড রান করবে
                if sound_enabled:
                    st.markdown('<audio src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" autoplay></audio>', unsafe_allow_html=True)

            elif rsi > 62 and price <= ema and trend <= 0:
                st.error("🔴 সংকেত: SELL (শর্ট পজিশন নিন)")
                st.info(f"💡 প্রস্তাবিত লট সাইজ: {dynamic_lot} Lots")
                
                if sound_enabled:
                    st.markdown('<audio src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" autoplay></audio>', unsafe_allow_html=True)

            else:
                st.warning("🟡 সংকেত: WAIT (অপেক্ষা করুন, এন্ট্রি অনুপযুক্ত)")
                st.info("💡 নিরাপদ থাকুন, ট্রেড থেকে বিরত থাকুন")
    else:
        st.error(f"{name} এর ডেটা আনতে সমস্যা হচ্ছে।")

    st.markdown("---")
