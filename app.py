import streamlit as st
# পেজ কনফিগারেশন
st.set_page_config(page_title="Forex & Gold Trend Dashboard", layout="wide")

# হেডার ও ইনফো
st.markdown("### Forex & Gold Trend Dashboard")
st.markdown("1m | 3m | 5m | 10m | 15m | 30m | 1h | 2h | 4h | 1d (প্রতি ১ মিনিটে স্বয়ংক্রিয়ভাবে আপডেট হবে)")
st.markdown("---")

# পেয়ারগুলোর তালিকা (এখানে গোল্ড 'XAU-USD' সহ প্রধান ফরেক্স পেয়ারগুলো যুক্ত করা হয়েছে)
# 'is_volatile': True হলে নিউজ বা হাই ভোলাটিলিটির কারণে সিগন্যাল সবুজ থাকলেও পেয়ারের নাম হলুদ হয়ে যাবে (ট্রেড নিষেধ)।
# 'is_volatile': False হলে এবং সিগন্যাল অনুকূলে থাকলে পেয়ারের নাম সবুজ দেখাবে (ট্রেড নেওয়া যাবে)।
pairs_data = [
    {
        "name": "XAU-USD (Gold)", 
        "is_volatile": False, 
        "signals": ["green", "green", "green", "green", "green", "green", "green", "green"]
    },
    {
        "name": "EUR-USD", 
        "is_volatile": False, 
        "signals": ["green", "green", "green", "green", "green", "green", "green", "green"]
    },
    {
        "name": "GBP-USD", 
        "is_volatile": True,  # হাই ভোলাটিলিটি / নো-ট্রেড জোন উদাহরণ
        "signals": ["green", "green", "green", "green", "green", "green", "green", "green"]
    },
    {
        "name": "USD-JPY", 
        "is_volatile": False, 
        "signals": ["green", "green", "green", "green", "green", "green", "green", "green"]
    },
    {
        "name": "BTC-USD", 
        "is_volatile": False, 
        "signals": ["green", "green", "green", "green", "green", "green", "green", "green"]
    }
]

# লুপ চালিয়ে ড্যাশবোর্ডে পেয়ার এবং সিগন্যাল ডটগুলো রেন্ডার করা
for pair in pairs_data:
    pair_name = pair["name"]
    is_volatile = pair["is_volatile"]
    signals = pair["signals"]
    
    # রঙের শর্ত: যদি মার্কেট ভোলাটাইল হয় বা নো-ট্রেড জোন থাকে, তবে সিগন্যাল সবুজ হলেও পেয়ারের নাম হলুদ হবে।
    if is_volatile:
        name_color = "#FFD700"  # হলুদ (সতর্কতা: ট্রেড থেকে বিরত থাকুন)
        status_note = " <span style='font-size: 12px; color: #FFD700;'>(⚠️ নো-ট্রেড জোন / ভোলাটাইল)</span>"
    else:
        name_color = "#2E8B57"  # সবুজ (ট্রেড নেওয়ার অনুকূল সময়)
        status_note = " <span style='font-size: 12px; color: #2E8B57;'>(✔ ট্রেড উপযোগী)</span>"
    
    # লেআউট কলাম তৈরি
    cols = st.columns([2, 5])
    
    with cols[0]:
        # পেয়ারের নাম নির্দিষ্ট রঙে রেন্ডার করা
        st.markdown(f"<h4 style='color: {name_color}; margin: 0;'>{pair_name}{status_note}</h4>", unsafe_allow_html=True)
    
    with cols[1]:
        # সিগন্যাল ডটগুলো রেন্ডার করা
        dots_html = " ".join(["🟢" if s == "green" else "🔴" for s in signals])
        st.markdown(f"<p style='margin: 5px 0 0 0; font-size: 18px;'>{dots_html}</p>", unsafe_allow_html=True)
        
    st.markdown("---")
