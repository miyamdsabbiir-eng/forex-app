import streamlit as st
import yfinance as yf


# পেজ সেটাপ ও লেআউট
st.set_page_config(
    page_title="Sabbir's Pro Smart Money Dashboard", 
    page_icon="⚡", 
    layout="wide"
)

# প্রিমিয়াম কাস্টম CSS ডিজাইন (খুব সুন্দর ও গোছানো ইন্টারফেসের জন্য)
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
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    .card-buyer {
        background: linear-gradient(145deg, #13221b 0%, #111827 100%);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #065f46;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    
    .card-seller {
        background: linear-gradient(145deg, #2b1317 0%, #111827 100%);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #991b1b;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);
    }
    
    .card-normal {
        background: linear-gradient(145deg, #1f293d 0%, #111827 100%);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #374151;
    }
    
    .pair-title { color: #60a5fa; font-size: 24px; font-weight: bold; }
    .price-text { color: #34d399; font-size: 20px; font-weight: bold; }
    .smart-money-text { color: #fbbf24; font-size: 15px; font-weight: bold; margin-top: 8px; }
</style>

<script>
function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'bn-BD';
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
    }
}
</script>
""", unsafe_allow_html=True)

# হেডার সেকশন
st.markdown("""
<div class="dashboard-header">
    <h1 style="color: #60a5fa; margin: 0; font-size: 28px;">⚡ সাব্বির ভাইয়ের প্রো স্মার্ট মানি ও ট্র্যাপ অ্যানালাইজার</h1>
    <p style="color: #9ca3af; margin-top: 8px; font-size: 16px;">রিয়েল-টাইম রিটেল প্রেশার, এসএল হান্টিং এবং লাইভ ভয়েস অ্যালার্ট সিস্টেম</p>
</div>
""", unsafe_allow_html=True)

# ভয়েস অ্যালার্ট কন্ট্রোল চেক বক্স
voice_alert = st.checkbox("📢 সাব্বির ভাইয়ের ভয়েস অ্যালার্ট চালু রাখুন (Active)", value=True)

# পেয়ারগুলোর তালিকা
symbols = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD"
}

# ডাটা ফেচ এবং ক্যালকুলেশন ফাংশন
@st.cache_data(ttl=30)
def get_market_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1h", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        if df.empty or len(df) < 14:
            return None, 50, 50, "স্বাভাবিক মার্কেট", 0.0, "নিউট্রাল", "normal"
            
        close_prices = df['Close'].squeeze()
        rsi = ta.momentum.RSIIndicator(close_prices, window=14).rsi().iloc[-1]
        
        current_price = float(close_prices.iloc[-1])
        prev_price = float(close_prices.iloc[-2])
        price_change = ((current_price - prev_price) / prev_price) * 100

        # পূর্ণসংখ্যায় পার্সেন্টেজ হিসাব
        buyer_pct = int(round(float(rsi)))
        if buyer_pct > 98: buyer_pct = 98
        if buyer_pct < 2: buyer_pct = 2
        seller_pct = int(100 - buyer_pct)

        # স্ট্যাটাস এবং কার্ডের স্টাইল নির্ধারণ
        if buyer_pct >= 75:
            status = "🟢 বায়ারের চাপ বেশি (Bull Trap / SL Hunt)"
            sm_action = "স্মার্ট মানি একটু উপরে গিয়ে বায়ারদের স্টপ লস হিট করে নিচে নামবে (Bearish Reversal)"
            card_type = "buyer"
        elif buyer_pct <= 25:
            status = "🔴 সেলারের চাপ বেশি (Bear Trap / SL Hunt)"
            sm_action = "স্মার্ট মানি একটু নিচে গিয়ে সেলারদের স্টপ লস হিট করে উপরে উঠবে (Bullish Reversal)"
            card_type = "seller"
        else:
            status = "⚖️ মার্কেট ব্যালেন্সড (Normal Market)"
            sm_action = "মার্কেট স্বাভাবিক রয়েছে"
            card_type = "normal"

        return current_price, buyer_pct, seller_pct, status, price_change, sm_action, card_type
    except Exception as e:
        return None, 50, 50, "ডেটা লোড ত্রুটি", 0.0, "অজানা", "normal"

# গ্রিড লেআউট তৈরি (২ কলাম বিশিষ্ট সুন্দর কার্ড)
cols = st.columns(2)
alert_messages = []

idx = 0
for name, sym in symbols.items():
    with cols[idx % 2]:
        price, buyer, seller, status, change, sm_action, card_type = get_market_data(sym)
        
        if price is not None:
            # কার্ডের স্টাইল সিলেক্ট করা (সবুজ বা লাল বর্ডার ও ব্যাকগ্রাউন্ড)
            css_class = "card-normal"
            if card_type == "buyer":
                css_class = "card-buyer"
            elif card_type == "seller":
                css_class = "card-seller"

            st.markdown(f"""
            <div class="{css_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="pair-title">{name}</span>
                    <span class="price-text">{price:.4f}</span>
                </div>
                <div style="color: #9ca3af; margin-top: 4px; font-size: 14px;">প্রাইস পরিবর্তন: {change:+.2f}%</div>
                <div style="margin-top: 10px; font-weight: bold; font-size: 16px;">{status}</div>
                <div class="smart-money-text">⚡ {sm_action}</div>
                <div style="margin-top: 12px; color: #d1d5db; font-size: 15px;">
                    🟢 রিটেল বায়ার: <b style="color: #34d399;">{buyer}%</b> &nbsp;&nbsp;|&nbsp;&nbsp; 🔴 রিটেল সেলার: <b style="color: #f87171;">{seller}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # প্রোগ্রেস বার
            st.progress(float(buyer / 100.0))

            # অতিরিক্ত চাপে ভয়েস অ্যালার্ট ট্রিগার করার নিয়ম
            if voice_alert and (buyer >= 80 or seller >= 80):
                if buyer >= 80:
                    alert_messages.append(f"সতর্কবার্তা! সাব্বির ভাই, {name} এ রিটেল বায়ারের চাপ {buyer} শতাংশ। স্মার্ট মানি একটু উপরে গিয়ে বায়ারদের স্টপ লস হিট করে আবার নিচে চলে আসবে!")
                elif seller >= 80:
                    alert_messages.append(f"সতর্কবার্তা! সাব্বির ভাই, {name} এ রিটেল সেলারের চাপ {seller} শতাংশ। স্মার্ট মানি একটু নিচে গিয়ে সেলারদের স্টপ লস হিট করে আবার উপরে চলে যাবে!")
        else:
            st.error(f"{name} এর ডেটা পাওয়া যায়নি।")
    idx += 1

# ভয়েস অ্যালার্ট ব্রাউজারে রান করার জাভাস্ক্রিপ্ট কোড
if voice_alert and alert_messages:
    msg = " ".join(alert_messages)
    st.markdown(f"""
    <script>
        speakText("{msg}");
    </script>
    """, unsafe_allow_html=True)

# রিফ্রেশ বাটন
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🔄 লাইভ মার্কেট আপডেট করুন", use_container_width=True):
        st.rerun()
