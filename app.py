import datetime
import pandas as pd
import requests
import streamlit as st
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
    [data-testid="stSidebar"] h1, h2, h3 { color: #0d47a1; }
    
    .stMetric { background-color: #f5f5f5; padding: 15px; border-radius: 10px; border: 2px solid #90caf9; color: #000000; }
    
    h1 { color: #0d47a1 !important; text-align: center; }
    h3 { color: #1976d2 !important; }

    .signal-box { padding: 18px; border-radius: 10px; margin-bottom: 10px; font-weight: bold; text-align: center; font-size: 16px; }
    .buy-signal { background-color: #e8f5e9; color: #2e7d32; border: 2px solid #66bb6a; }
    .sell-signal { background-color: #ffebee; color: #c62828; border: 2px solid #ef5350; }
    .wait-signal { background-color: #fffde7; color: #f9a825; border: 2px solid #ffee58; }
    </style>
""",
    unsafe_allow_html=True,
)

# ৩. সাইডবার কনফিগারেশন
with st.sidebar:
    st.header("🚦 ট্রাফিক লাইট সিগন্যাল কন্ট্রোল")
    account_balance = st.number_input(
        "আপনার মোট ব্যালেন্স ($)", min_value=10.0, value=100.0, step=10.0
    )
    st.markdown("""
    * **🟢 সবুজ:** শতভাগ ভরসা নিয়ে **বাই (Buy)** নিন।
    * **🔴 লাল:** আত্মবিশ্বাসের সাথে **সেল (Sell)** নিন।
    * **🟡 হলুদ:** মার্কেট ঝুঁকিপূর্ণ, **ট্রেড নেওয়া নিষেধ** (অপেক্ষা করুন)।
    """)

st.title("🚦 ফরেক্স ট্রাফিক লাইট সিগন্যাল ড্যাশবোর্ড")
st.write(
    "রং দেখে সিদ্ধান্ত নিন: সবুজ = বাই, লাল = সেল, হলুদ = নিরাপদ দূরত্বে থাকুন।"
)


# ৪. ডেটা ফেচিং ও ফিল্টার ফাংশন
def get_traffic_signal_data(symbol):
  try:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1h"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()

    result = data["chart"]["result"][0]
    meta = result["meta"]
    current_price = meta["regularMarketPrice"]
    previous_close = meta["chartPreviousClose"]

    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100

    timestamps = result["timestamp"]
    quotes = result["indicators"]["quote"][0]["close"]

    df = pd.DataFrame({"time": timestamps, "close": quotes})
    df = df.dropna()

    if len(df) > 14:
      delta = df["close"].diff()
      gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
      rs = gain / loss
      rsi = 100 - (100 / (1 + rs))
      current_rsi = rsi.iloc[-1]

      ema_20 = df["close"].ewm(span=20, adjust=False).mean().iloc[-1]
      recent_trend = df["close"].iloc[-1] - df["close"].iloc[-3]
      volatility = df["close"].pct_change().std() * 100
    else:
      current_rsi = 50.0
      ema_20 = current_price
      recent_trend = 0
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
@st.fragment(run_every=60)
def render_dashboard():
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
          signal_html = f"""
                    <div class="signal-box buy-signal">
                        🟢 বাই (Buy) নিন - সবুজ সংকেত!<br>
                        <span style="font-size: 13px; color: #1b5e20;">ভরসা করে বাই ধরতে পারেন • লট: <b>{dynamic_lot}</b></span>
                    </div>
                    """
        elif rsi > 62 and price <= ema and trend <= 0:
          signal_html = f"""
                    <div class="signal-box sell-signal">
                        🔴 সেল (Sell) নিন - লাল সংকেত!<br>
                        <span style="font-size: 13px; color: #b71c1c;">ভরসা করে সেল ধরতে পারেন • লট: <b>{dynamic_lot}</b></span>
                    </div>
                    """
        else:
          signal_html = """
                    <div class="signal-box wait-signal">
                        🟡 ট্রেড নিষিদ্ধ - হলুদ সংকেত!<br>
                        <span style="font-size: 13px; color: #f57f17;">মার্কেট ঝুঁকিপূর্ণ, এখন কোনো ট্রেড নেবেন না</span>
                    </div>
                    """

        st.markdown(signal_html, unsafe_allow_html=True)

      st.markdown("---")
    else:
      st.error(f"{name} এর ডেটা আনতে সমস্যা হচ্ছে।")


# রেন্ডার কল
render_dashboard()



