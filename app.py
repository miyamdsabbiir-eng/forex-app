import streamlit as st
import pandas as pd
import requests
import time

# পেজ কনফিগারেশন
st.set_page_config(
    page_title="Sabbir's Ultimate Pro Forex Dashboard",
    page_icon="📈",
    layout="wide"
)

# প্রিমিয়াম, মডার্ন এবং মোটা প্রোগ্রেস বার সহ চমৎকার CSS স্টাইলিং
st.markdown("""
    <style>
    .main { background-color: #070913; color: #ffffff; }
    .stApp { background-color: #070913; }
    
    .main-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 25px;
    }
    
    .card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    
    .alert-buy {
        background: linear-gradient(90deg, #064e3b 0%, #022c22 100%);
        padding: 16px;
        border-radius: 14px;
        border-left: 6px solid #34d399;
        margin-bottom: 12px;
        color: #a7f3d0;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(6,78,59,0.3);
    }
    
    .alert-sell {
        background: linear-gradient(90deg, #451a03 0%, #291002 100%);
        padding: 16px;
        border-radius: 14px;
        border-left: 6px solid #f87171;
        margin-bottom: 12px;
        color: #fca5a5;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(69,26,3,0.3);
    }
    
    .pair-title { color: #60a5fa; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
    .price-text { color: #34d399; font-size: 20px; font-weight: 700; }
    
    /* সেন্টিমেন্ট প্রোগ্রেস বারটিকে মোটা ও সুন্দর করার জন্য */
    .stProgress > div > div > div > div {
        height: 16px !important;
        border-radius: 10px !important;
        background: linear-gradient(90deg, #34d399, #60a5fa);
    }
    .stProgress > div > div > div {
        height: 16px !important;
        border-radius: 10px !important;
        background-color: #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 সাব্বির ভাইয়ের ফুল অটো স্মার্ট মানি ও সেন্টিমেন্ট ড্যাশবোর্ড</div>', unsafe_allow_html=True)

# ব্রাউজার ভয়েস অ্যালার্ট ফাংশন
def trigger_voice_alert(message):
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{message}");
        msg.rate = 1.0;
        msg.pitch = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# অ্যাপে প্রথমবার প্রবেশ করার সাথে সাথেই স্পিকারে বলার জন্য ওয়েলকাম ভয়েস লজিক
if 'welcomed' not in st.session_state:
    st.session_state.welcomed = True
    trigger_voice_alert("স্বাগতম সাব্বির ভাই! আপনার ফুল অটো স্মার্ট মানি এবং ফরেক্স ড্যাশবোর্ড চালু হয়েছে।")

# টপ স্ট্যাটাস বার
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="সিস্টেম স্ট্যাটাস", value="ফুল অটো মোড", delta="স্বয়ংক্রিয় আপডেট")
with col2:
    st.metric(label="সেন্টিমেন্ট মোড", value="ব্যালেন্সড ও ন্যাচারাল")
with col3:
    st.metric(label="স্পিকার ভয়েস", value="সক্রিয় (Active)", delta="🔊 On")

st.markdown("---")

symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "AUDUSD=X"]

# ব্যালেন্সড সেন্টিমেন্ট ও ডেটা ফেচিং ফাংশন
def get_forex_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = data['chart']['result'][0]
            meta = result['meta']
            price = meta['regularMarketPrice']
            prev_close = meta['chartPreviousClose']
            change = ((price - prev_close) / prev_close) * 100
            
            # সেন্টিমেন্ট ব্যালেন্সড রেঞ্জ
            base_sentiment = 50 + int(change * 15)
            if base_sentiment > 72: buyer_pct = 72
            elif base_sentiment < 28: buyer_pct = 28
            else: buyer_pct = base_sentiment
            
            seller_pct = 100 - buyer_pct
            
            # স্মার্ট মানি ডিরেকশন
            if change >= 0:
                sm_direction = "BUY (Institutional Bullish Trend)"
                sm_color_tag = "green"
            else:
                sm_direction = "SELL (Institutional Bearish Trend)"
                sm_color_tag = "red"
                
            return price, buyer_pct, seller_pct, sm_direction, sm_color_tag, change
    except Exception as e:
        pass
    return None, 50, 50, "Neutral", "gray", 0.0

# প্রতি ১ মিনিট পরপর ফুল অটো আপডেট ফ্রেমওয়ার্ক (কোনো ম্যানুয়াল বাটনের প্রয়োজন নেই)
@st.fragment(run_every=60)
def auto_dashboard():
    st.caption(f"⏱️ সর্বশেষ আপডেট: {time.strftime('%I:%M:%S %p')} | সিস্টেম সম্পূর্ণ অটোমেটিক লাইভ মোডে চলছে...")
    
    cols = st.columns(2)
    idx = 0
    
    for sym in symbols:
        if sym == "EURUSD=X": display_name = "EUR/USD"
        elif sym == "GBPUSD=X": display_name = "GBP/USD"
        elif sym == "USDJPY=X": display_name = "USD/JPY"
        elif sym == "USDCAD=X": display_name = "USD/CAD"
        elif sym == "AUDUSD=X": display_name = "AUD/USD"

        price, buyer, seller, sm_direction, sm_color_tag, change = get_forex_data(sym)
        
        with cols[idx % 2]:
            if price is not None:
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="pair-title">{display_name}</span>
                        <span class="price-text">{price:.4f}</span>
                    </div>
                    <div style="color: #94a3b8; margin-top: 6px; font-size: 14px;">মার্কেট পরিবর্তন: <b style="color: {'#34d399' if change>=0 else '#f87171'};">{change:+.2f}%</b></div>
                    <div style="margin-top: 10px; font-size: 15px;"><b>স্মার্ট মানি ডিরেকশন:</b> <span style="color: {'#34d399' if sm_color_tag=='green' else '#f87171'}; font-weight: bold;">{sm_direction}</span></div>
                    <div style="margin-top: 10px; color: #e2e8f0; font-size: 14px;">
                        🟢 বায়ার সেন্টিমেন্ট: <b style="color: #34d399;">{buyer}%</b> &nbsp;|&nbsp; 🔴 সেলার সেন্টিমেন্ট: <b style="color: #f87171;">{seller}%</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # মোটা এবং সুন্দর প্রোগ্রেস বার
                st.progress(float(buyer / 100.0))
                
                # স্মার্ট মানি বাই বা সেল অ্যালার্ট এবং ভয়েস
                if sm_color_tag == 'green':
                    alert_text = f"সাব্বیر ভাই! {display_name} পেয়ারে স্মার্ট মানি বাই এন্ট্রি নিয়েছে!"
                    st.markdown(f'<div class="alert-buy">🟢 <b>স্মার্ট মানি বাই সিগন্যাল:</b> {alert_text}</div>', unsafe_allow_html=True)
                    trigger_voice_alert(alert_text)
                else:
                    alert_text = f"সাব্বির ভাই! {display_name} পেয়ারে স্মার্ট মানি সেল এন্ট্রি নিয়েছে!"
                    st.markdown(f'<div class="alert-sell">🔴 <b>স্মার্ট মানি সেল সিগন্যাল:</b> {alert_text}</div>', unsafe_allow_html=True)
                    trigger_voice_alert(alert_text)
                    
                # সেন্টিমেন্ট ট্র্যাপ অ্যালার্ট
                if buyer >= 70:
                    trap_text = f"সাব্বির ভাই! {display_name} পেয়ারে রিটেইলদের বাই চাপ বেড়ে সত্তরের ওপরে গেছে!"
                    st.markdown(f'<div class="alert-sell">⚠️ <b>সেন্টিমেন্ট অ্যালার্ট:</b> {trap_text}</div>', unsafe_allow_html=True)
                    trigger_voice_alert(trap_text)
                elif seller >= 70:
                    trap_text = f"সাব্বির ভাই! {display_name} পেয়ারে রিটেইলদের সেল চাপ বেড়ে সত্তরের ওপরে গেছে!"
                    st.markdown(f'<div class="alert-sell">⚠️ <b>সেন্টিমেন্ট অ্যালার্ট:</b> {trap_text}</div>', unsafe_allow_html=True)
                    trigger_voice_alert(trap_text)
            else:
                st.error(f"{display_name} এর ডেটা লোড করতে সমস্যা হচ্ছে।")
        idx += 1

auto_dashboard()

