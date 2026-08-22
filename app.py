
import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Forex Live Tracker", layout="centered")

st.markdown("<h2 style='text-align: center; color: #00d2ff;'>Forex Live Sentiment</h2>", unsafe_allow_html=True)

currency_tickers = {
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'USD/JPY': 'JPY=X',
    'AUD/USD': 'AUDUSD=X',
    'USD/CAD': 'CAD=X'
}

for pair, ticker in currency_tickers.items():
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False)
        if df.empty:
            continue
        close_prices = df['Close'].squeeze()
        price = float(close_prices.iloc[-1])
        
        rsi = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi().iloc[-1]
        buy_percent = 50.0 if pd.isna(rsi) else round(float(rsi), 1)
        sell_percent = round(100 - buy_percent, 1)
        
        price_format = f"{price:.3f}" if ("JPY" in pair or "CAD" in pair) else f"{price:.5f}"
        
        st.markdown(f'''
        <div style="background-color: #12181b; border: 1px solid #2a3b4c; border-radius: 10px; padding: 12px; margin-bottom: 12px; color: white;">
            <div style="display: flex; justify-content: space-between;">
                <b style="color: #00d2ff; font-size: 18px;">{pair}</b>
                <b style="color: #00e676;">দাম: {price_format}</b>
            </div>
            <div style="margin-top: 8px; font-size: 12px; display: flex; justify-content: space-between;">
                <span style="color: #4caf50;">🟢 বায়ার: {buy_percent}%</span>
                <span style="color: #f44336;">🔴 সেলার: {sell_percent}%</span>
            </div>
            <div style="width: 100%; background-color: #f44336; border-radius: 6px; height: 8px; margin-top: 6px; overflow: hidden;">
                <div style="width: {buy_percent}%; background-color: #4caf50; height: 100%;"></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    except Exception:
        continue
