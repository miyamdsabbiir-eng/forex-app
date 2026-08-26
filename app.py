import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Sabbir's Forex Sentiment Dashboard", 
    page_icon="📊", 
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .stApp { background-color: #0b0f19; color: #ffffff; }
    .dashboard-header {
        background: linear-gradient(135deg, #1f293d 0%, #111827 100%);
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #1f2937;
        text-align: center;
        margin-bottom: 25px;
    }
    .card-style {
        background: linear-gradient(145deg, #1f293d 0%, #111827 100%);
        border-radius: 16px; padding: 20px; margin-bottom: 20px;
        border: 1px solid #374151;
    }
    .pair-title { color: #60a5fa; font-size: 22px; font-weight: bold; }
    .price-text { color: #34d399; font-size: 18px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dashboard-header">
    <h1 style="color: #60a5fa; margin: 0; font-size: 26px;">📊 সাব্বির ভাইয়ের প্রফেশনাল ফরেক্স সেন্টিমেন্ট ড্যাশবোর্ড</h1>
    <p style="color: #9ca3af; margin-top: 5px;">এক্সেল স্টাইল স্টেবল মার্কেট ও বায়ার-সেলার চাপ অ্যানালাইসিস</p>
</div>
""", unsafe_allow_html=True)

symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "AUDUSD=X"]

@st.cache_data(ttl=15)
def get_forex_sentiment(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            data = response.json()
            result = data['chart']['result'][0]
            meta = result['meta']
            price = meta['regularMarketPrice']
            prev_close = meta['chartPreviousClose']
            change = ((price - prev_close) / prev_close) * 100
            
            base_sentiment = 50 + int(change * 2.5)
            
            if base_sentiment > 72: buyer_pct = 72
            elif base_sentiment < 28: buyer_pct = 28
            else: buyer_pct = base_sentiment
            
            seller_pct = 100 - buyer_pct
            
            if buyer_pct > 50:
                status = "🟢 বায়ারের শক্তিশালী সেন্টিমেন্ট"
            else:
                status = "🔴 সেলারের শক্তিশালী সেন্টিমেন্ট"
                
            return price, buyer_pct, seller_pct, status, change
    except Exception as e:
        pass
    return None, 50, 50, "ডেটা লোড হচ্ছে...", 0.0

cols = st.columns(2)
idx = 0

for sym in symbols:
    if sym == "EURUSD=X": display_name = "EUR/USD"
    elif sym == "GBPUSD=X": display_name = "GBP/USD"
    elif sym == "USDJPY=X": display_name = "USD/JPY"
    elif sym == "USDCAD=X": display_name = "USD/CAD"
    elif sym == "AUDUSD=X": display_name = "AUD/USD"

    with cols[idx % 2]:
        price, buyer, seller, status, change = get_forex_sentiment(sym)
        
        if price is not None:
            st.markdown(f"""
            <div class="card-style">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="pair-title">{display_name}</span>
                    <span class="price-text">{price:.4f}</span>
                </div>
                <div style="color: #9ca3af; margin-top: 5px; font-size: 14px;">দৈনিক পরিবর্তন: {change:+.2f}%</div>
                <div style="margin-top: 8px; font-weight: bold;">{status}</div>
                <div style="margin-top: 8px; color: #d1d5db; font-size: 14px;">
                    🟢 বায়ার সেন্টিমেন্ট: <b style="color: #34d399;">{buyer}%</b> &nbsp;|&nbsp; 🔴 সেলার সেন্টিমেন্ট: <b style="color: #f87171;">{seller}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(float(buyer / 100.0))
        else:
            st.error(f"{display_name} এর লাইভ ডেটা আনতে সমস্যা হচ্ছে।")
    idx += 1

st.markdown("---")
if st.button("🔄 ফরেক্স সেন্টিমেন্ট আপডেট করুন", use_container_width=True):
    st.rerun()
