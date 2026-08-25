importt streamlit as st
import yfinance as yf
import pandas as pd
import taimportt time

# পেজ সেটআপ
st.set_page_config(page_title="Sabbir's Multi-Asset Alert", layout="centered")

# কাস্টম CSS ডিজাইন এবং বাংলা ভয়েস অ্যালার্ট স্ক্রিপ্ট
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .card {
        background-color: #161b22;
        border-radius: 15px;
        padding: 15px 20px;
        margin-bottom: 15px;
        border: 1px solid #30363d;
    }
    .pair-title { color: #58a6ff; font-size: 20px; font-weight: bold; }
    .price-text { color: #3fb950; font-size: 18px; font-weight: bold; float: right; }
    .stats-text { color: #8b949e; font-size: 14px; margin-top: 5px; }
    .smart-money { color: #f0883e; font-weight: bold; }
</style>

<script>
function speakSabbirAlert(text) {
    if ('speechSynthesis' in window) {
        let utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'bn-BD';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }
}
</script>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #33c3f0;'>Forex & Crypto Sentiment Alert</h1>", unsafe_allow_html=True)
st.write("")

voice_alert = st.checkbox("📢 সাব্বির ভাইয়ের ভয়েস অ্যালার্ট চালু রাখুন (Active)", value=True)

# অ্যাসেট তালিকা
currency_tickers = {
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'USD/JPY': 'USDJPY=X',
    'AUD/USD': 'AUDUSD=X',
    'USD/CAD': 'USDCAD=X',
    'NZD/USD': 'NZDUSD=X',
    'EUR/GBP': 'EURGBP=X',
    'EUR/JPY': 'EURJPY=X',
    'GBP/JPY': 'GBPJPY=X',
    'Bitcoin (BTC)': 'BTC-USD',
    'Ethereum (ETH)': 'ETH-USD',
    'Solana (SOL)': 'SOL-USD',
    'Gold (XAU)': 'GC=F'
}

placeholder = st.empty()

while True:
    with placeholder.container():
        for name, ticker in currency_tickers.items():
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="5d", interval="1h")
                
                if not hist.empty and len(hist) > 14:
                    close_prices = hist['Close']
                    rsi = ta.momentum.RSIIndicator(close_prices, window=14).rsi().iloc[-1]
                    
                    curr_price = close_prices.iloc[-1]
                    open_price = hist['Open'].iloc[0]
                    change = ((curr_price - open_price) / open_price) * 100
                    
                    if rsi > 60 or change > 0.04:
                        buy_pct = 85.0
                        sell_pct = 15.0
                        zone_text = "🟢 বায়ারের চাপ বেশি (Buyer Heavy)"
                        is_trap = True
                        trap_type = "BUY"
                    elif rsi < 40 or change < -0.04:
                        buy_pct = 15.0
                        sell_pct = 85.0
                        zone_text = "🔴 সেলারের চাপ বেশি (Seller Heavy)"
                        is_trap = True
                        trap_type = "SELL"
                    else:
                        buy_pct = 50.0
                        sell_pct = 50.0
                        zone_text = "🟡 মার্কেট ব্যালেন্সড (Balanced)"
                        is_trap = False
                        trap_type = "NONE"
                else:
                    curr_price = 0.0
                    buy_pct = 50.0
                    sell_pct = 50.0
                    zone_text = "⏳ ডেটা লোড হচ্ছে..."
                    is_trap = False
                    trap_type = "NONE"
            except:
                curr_price = 0.0
                buy_pct = 50.0
                sell_pct = 50.0
                zone_text = "⚠️ কানেকশন সমস্যা"
                is_trap = False
                trap_type = "NONE"
            
            st.markdown(f"""
                <div class="card">
                    <span class="pair-title">{name}</span>
                    <span class="price-text">দাম: {curr_price:.4f}</span>
                    <div class="stats-text">
                        <span class="smart-money">{zone_text}</span><br>
                        🟢 বায়ার: {buy_pct}% &nbsp;&nbsp;&nbsp;&nbsp; 🔴 সেলার: {sell_pct}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.progress(int(buy_pct))
            
            if voice_alert and is_trap and (buy_pct >= 80.0 or sell_pct >= 80.0):
                if trap_type == "BUY":
                    voice_msg = f"সাব্বির ভাই, {name} পেয়ারে বায়ারের চাপ আশি পার্সেন্টের বেশি রয়েছে।"
                else:
                    voice_msg = f"সাব্বির ভাই, {name} পেয়ারে সেলারের চাপ আশি পার্সেন্টের বেশি রয়েছে।"
                
                st.markdown(f"""
                    <script>
                        speakSabbirAlert("{voice_msg}");
                    </script>
                """, unsafe_allow_html=True)
            
        time.sleep(25)
        st.rerun()
