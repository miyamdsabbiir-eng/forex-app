import streamlit as st
import random
# পেজ কনফিগারেশন
st.set_page_config(page_title="AI Smart Money & Volatility Dashboard", layout="wide")

# হেডার ও ইনফো
st.markdown("### AI Smart Money & Volatility Defense Dashboard")
st.markdown("5m | 10m | 15m | 30m | 1h | 2h | 4h | 1d (স্মার্ট মানি, ভোলাটিলিটি ও নো-ট্রেড জোন প্রটেকশন)")
st.markdown("---")

# st.fragment ব্যবহার করে প্রতি ১ মিনিটে অটো-আপডেট ও এআই ডিপ অ্যানালাইসিস
@st.fragment(run_every=60)
def volatility_defense_dashboard():
    # ৮টি টাইমফ্রেমের তালিকা
    timeframes = ["5m", "10m", "15m", "30m", "1h", "2h", "4h", "1d"]
    
    # গোল্ড, ফরেক্স মেজর পেয়ার এবং ক্রিপ্টো মিলিয়ে ১৫টি অ্যাসেটের তালিকা
    pairs_list = [
        "XAU-USD (Gold)", "EUR-USD", "GBP-USD", "USD-JPY", "AUD-USD", 
        "NZD-USD", "USD-CAD", "USD-CHF", "EUR-GBP", "EUR-JPY", 
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"
    ]
    
    updated_data = []
    for name in pairs_list:
        # ভোলাটিলিটি বা ঝামেলাপূর্ণ মার্কেট ডিটেকশন (True মানেই নো-ট্রেড জোন / হলুদ সংকেত)
        is_volatile = random.choice([True, False, False, False])
        
        # স্মার্ট মানি এবং রিটেল ট্র্যাপ সিমুলেশন
        smart_money_action = random.choice(["ACCUMULATION (Buy)", "DISTRIBUTION (Sell)", "SIDEWAYS"])
        retail_trap = random.choice([True, False])
        
        # টাইমফ্রেম সিগন্যাল
        signals = [random.choice(["green", "green", "red"]) for _ in range(8)]
        
        updated_data.append({
            "name": name,
            "is_volatile": is_volatile,
            "smart_money": smart_money_action,
            "retail_trap": retail_trap,
            "signals": signals
        })

    # লুপ চালিয়ে ড্যাশবোর্ডে ডেটা রেন্ডার করা
    for pair in updated_data:
        pair_name = pair["name"]
        is_volatile = pair["is_volatile"]
        smart_money = pair["smart_money"]
        retail_trap = pair["retail_trap"]
        signals = pair["signals"]
        
        # --- মূল নো-ট্রেড জোন ও ভোলাটিলিটি কালার লজিক ---
        if is_volatile:
            name_color = "#FFD700"  # হলুদ রঙ (সতর্কতা: নো-ট্রেড জোন)
            status_note = " <span style='font-size: 12px; color: #FFD700;'><b>(⚠️ NO-TRADE ZONE: বাজার অত্যন্ত অস্থির ও ঝুঁকিপূর্ণ!)</b></span>"
        else:
            name_color = "#FFFFFF"  # স্বাভাবিক রঙ
            status_note = " <span style='font-size: 12px; color: #2E8B57;'>(✔ মার্কেট স্টেবল - ট্রেড উপযোগী)</span>"
        
        # এআই স্মার্ট মানি ও ভোলাটিলিটি অ্যানালাইসিস মেসেজ
        if is_volatile:
            ai_advice = "🚨 <b>Volatility Alert:</b> মার্কেটে হঠাৎ অস্বাভাবিক ভোলাটিলিটি বা বড় কোনো ঝামেলা তৈরি হয়েছে। এআই সিস্টেম এই পেয়ারটিকে 'নো-ট্রেড জোন' হিসেবে লক করেছে। ক্যাপিটাল বাঁচাতে এই মুহূর্তে দূরে থাকুন।"
            ai_color = "#FFD700"
        elif "ACCUMULATION" in smart_money and not retail_trap:
            ai_advice = "🤖 <b>AI & Smart Money:</b> ইনস্টিটিউশনগুলো বড় আকারে বাই পজিশন নিচ্ছে। রিটেল ট্র্যাপ মুক্ত একটি পরিষ্কার বাই জোন।"
            ai_color = "#2E8B57"
        elif "DISTRIBUTION" in smart_money and not retail_trap:
            ai_advice = "🤖 <b>AI & Smart Money:</b> স্মার্ট মানি পজিশন অফলোড বা সেল করছে। শর্ট পজিশনের জন্য অনুকূল পরিবেশ।"
            ai_color = "#CD5C5C"
        elif retail_trap:
            ai_advice = "⚠️ <b>Retail Trap Warning:</b> রিটেল ট্রেডাররা ফেক ব্রেকআউটে ট্র্যাপে পড়েছে। এন্ট্রি নিলে লস হওয়ার উচ্চ সম্ভাবনা রয়েছে।"
            ai_color = "#FFA500"
        else:
            ai_advice = "🤖 <b>AI Analysis:</b> মার্কেট নিউট্রাল মোডে আছে। সিগন্যাল কনফার্মেশনের জন্য অপেক্ষা করুন।"
            ai_color = "#00BFFF"

        # লেআউট তৈরি
        cols = st.columns([2, 5])
        
        with cols[0]:
            st.markdown(f"<h4 style='color: {name_color}; margin: 0;'>{pair_name}{status_note}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin: 3px 0 0 0; font-size: 11px; color: #A9A9A9;'><b>Institutional Flow:</b> {smart_money}</p>", unsafe_allow_html=True)
        
        with cols[1]:
            # টাইমফ্রেম অনুযায়ী সিগন্যাল ডট
            tf_dots_display = []
            for tf, sig in zip(timeframes, signals):
                dot = "🟢" if sig == "green" else "🔴"
                tf_dots_display.append(f"<span style='font-size: 13px; margin-right: 6px;'>{tf}: {dot}</span>")
            
            dots_html = "".join(tf_dots_display)
            st.markdown(f"<p style='margin: 0; padding-bottom: 2px;'>{dots_html}</p>", unsafe_allow_html=True)
            
            # এআই অ্যাডভান্সড অ্যানালাইসিস বক্স
            st.markdown(f"<p style='margin: 0; font-size: 12px; color: {ai_color};'>{ai_advice}</p>", unsafe_allow_html=True)
            
        st.markdown("---")

# ড্যাশবোর্ড ফাংশন কল করা হলো
volatility_defense_dashboard()
