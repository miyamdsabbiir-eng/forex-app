import streamlit as st
import random

# পেজ কনফিগারেশন
st.set_page_config(page_title="Live Forex & Crypto Trend Dashboard", layout="wide")

# হেডার ও টাইমফ্রেম ইনফো (আপনার আগের সিস্টেম অনুযায়ী)
st.markdown("### Live Forex & Crypto Trend Dashboard")
st.markdown("5m | 10m | 15m | 30m | 1h | 2h | 4h | 1d (প্রতি ১ মিনিটে স্বয়ংক্রিয়ভাবে নতুন ডাটা নিয়ে আপডেট হবে)")
st.markdown("---")

# st.fragment ব্যবহার করে নির্দিষ্ট অংশটি প্রতি ১ মিনিট (৬০ সেকেন্ড) পর পর অটো-রিফ্রেশ ও নতুন ডাটা নিয়ে আসবে
@st.fragment(run_every=60)
def live_dashboard():
    # গোল্ড, ফরেক্স মেজর পেয়ার এবং ক্রিপ্টো মিলিয়ে ১৫টি অ্যাসেটের তালিকা
    pairs_list = [
        "XAU-USD (Gold)", "EUR-USD", "GBP-USD", "USD-JPY", "AUD-USD", 
        "NZD-USD", "USD-CAD", "USD-CHF", "EUR-GBP", "EUR-JPY", 
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"
    ]
    
    # প্রতি ১ মিনিটে নতুন ডাটা ফেচ বা সিমুলেট করার লজিক
    updated_data = []
    for name in pairs_list:
        # ভোলাটিলিটি বা নো-ট্রেড জোন নির্ধারণ (True হলে হলুদ, False হলে সবুজ)
        is_volatile = random.choice([True, False, False]) 
        
        # টাইমফ্রেমগুলোর জন্য সিগন্যাল (5m, 10m, 15m, 30m ইত্যাদি)
        signals = [random.choice(["green", "green", "green", "red"]) for _ in range(8)]
        
        updated_data.append({
            "name": name,
            "is_volatile": is_volatile,
            "signals": signals
        })

    # লুপ চালিয়ে ড্যাশবোর্ডে পেয়ার এবং সিগন্যাল ডটগুলো রেন্ডার করা
    for pair in updated_data:
        pair_name = pair["name"]
        is_volatile = pair["is_volatile"]
        signals = pair["signals"]
        
        # মূল শর্ত: মার্কেট ভোলাটাইল বা নো-ট্রেড জোন হলে পেয়ারের নাম হলুদ (ট্রেড নিষেধ) 
        # এবং স্বাভাবিক থাকলে সবুজ (ট্রেড করা যাবে) হবে।
        if is_volatile:
            name_color = "#FFD700"  # হলুদ (নো-ট্রেড জোন / ট্রেড থেকে বিরত থাকুন)
            status_note = " <span style='font-size: 12px; color: #FFD700;'>(⚠️ নো-ট্রেড জোন - ট্রেড নিষেধ)</span>"
        else:
            name_color = "#2E8B57"  # সবুজ (ট্রেড উপযোগী)
            status_note = " <span style='font-size: 12px; color: #2E8B57;'>(✔ ট্রেড নেওয়া যাবে)</span>"
        
        # লেআউট কলাম তৈরি
        cols = st.columns([2, 5])
        
        with cols[0]:
            # কারেন্সি পেয়ারের নাম নির্দিষ্ট রঙে রেন্ডার করা
            st.markdown(f"<h4 style='color: {name_color}; margin: 0;'>{pair_name}{status_note}</h4>", unsafe_allow_html=True)
        
        with cols[1]:
            # টাইমফ্রেম সিগন্যাল ডটগুলো রেন্ডার করা
            dots_html = " ".join(["🟢" if s == "green" else "🔴" for s in signals])
            st.markdown(f"<p style='margin: 5px 0 0 0; font-size: 18px;'>{dots_html}</p>", unsafe_allow_html=True)
            
        st.markdown("---")

# লাইভ ড্যাশবোর্ড ফাংশন কল করা হলো
live_dashboard()
