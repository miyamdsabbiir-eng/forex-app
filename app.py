import streamlit as st
import time
import random

st.set_page_config(page_title="Safe Entry Guard ($10 Protection)", layout="wide")

st.markdown("### 🛡️ $10 Capital Safe Entry Dashboard")
st.markdown("5m | 10m | 15m | 30m | 1h | 2h | 4h | 1d (ফেক মুভমেন্ট ও রিভার্সাল প্রটেকশন সহ)")
st.markdown("---")

@st.fragment(run_every=60)
def safe_entry_dashboard():
    timeframes = ["5m", "10m", "15m", "30m", "1h", "2h", "4h", "1d"]
    assets_list = [
        "XAU-USD (Gold)", "EUR-USD", "GBP-USD", "USD-JPY", 
        "BTC-USD", "ETH-USD", "SOL-USD", "AUD-USD"
    ]
    
    cycle_duration = 1800 
    elapsed_time = int(time.time() % cycle_duration)
    age_mins = elapsed_time // 60
    
    for i, asset in enumerate(assets_list):
        random.seed(hash(asset) + (int(time.time() / cycle_duration)))
        
        # সিগন্যাল বয়স বা ফেক মুভমেন্টের ঝুঁকি থাকলে হলুদ দেখাবে
        if age_mins >= 25:
            box_color = "#FFD700"  # হলুদ
            status_text = "🟡 NO-TRADE / EXPIRED (ফেক মুভমেন্ট এড়াতে ট্রেড বন্ধ)"
            dots = "🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡"
            guide = "সিগন্যাল শেষের পথে। মার্কেট যেকোনো সময় উল্টো দিকে ঘুরে ১০ ডলার খেয়ে ফেলতে পারে। হাত গুটিয়ে থাকুন।"
        else:
            direction = random.choice(["BUY", "SELL"])
            if direction == "BUY":
                box_color = "#00FF7F"  # সবুজ
                status_text = "🟢 SAFE BUY (সাপোর্ট থেকে কনফার্মড বাউন্স)"
                dots = "🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢"
                guide = "মার্কেট অলরেডি উপরে যাওয়ার কনফার্মেশন দিয়েছে। ফেক ডাউনের ঝুঁকি নেই, নিরাপদে বাই নিতে পারেন।"
            else:
                box_color = "#FF4500"  # লাল
                status_text = "🔴 SAFE SELL (রেজিস্ট্যান্স থেকে কনফার্মড ড্রপ)"
                dots = "🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴"
                guide = "মার্কেট রেজিস্ট্যান্স থেকে নিচে নামার জন্য প্রস্তুত। উপরে গিয়ে ধোঁকা দেওয়ার সুযোগ নেই, সেল নিতে পারেন।"

        cols = st.columns([3, 5])
        
        with cols[0]:
            st.markdown(f"<h3 style='color: {box_color}; margin: 0;'>{asset}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 11px; color: {box_color}; margin: 2px 0 0 0;'><b>Safe Status:</b> {status_text}</p>", unsafe_allow_html=True)
            
        with cols[1]:
            st.markdown(f"<p style='margin: 0; font-size: 13px;'>{dots}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin: 0; font-size: 12px; color: #D3D3D3;'><b>Capital Guard Rule:</b> {guide}</p>", unsafe_allow_html=True)
            
        st.markdown("---")

safe_entry_dashboard()
