import streamlit as st
import pandas as pd

from scanner.universe import load_stocks, get_stock_price
from scanner.recommendation import get_recommendation
from scanner.intraday_tradeplan import get_intraday_tradeplan

st.set_page_config(
    page_title="SMART F&O ENGINE V2",
    layout="wide"
)

@st.cache_data(ttl=300)
def cached_price(stock):
    return get_stock_price(stock)

@st.cache_data(ttl=300)
def cached_recommendation(stock):
    return get_recommendation(stock)

@st.cache_data(ttl=300)
def cached_tradeplan(stock, action):
    return get_intraday_tradeplan(stock, action)

st.title("SMART F&O DECISION ENGINE V2")

if st.button("🔄 Refresh Scanner"):
    st.cache_data.clear()
    st.rerun()

stocks = load_stocks()

results = []

for stock in stocks:

    price = cached_price(stock)

    if price is None:
        continue

    if price < 2500:
        continue

    action, confidence, entry_window = cached_recommendation(stock)

    if action not in ["BUY", "SELL"]:
        continue

    if confidence < 75:
        continue

    entry, sl, target, rr, setup_time = cached_tradeplan(stock, action)

    # Only confirmed trades
    if entry is None:
        continue

    results.append({
        "Stock": stock,
        "Status": "READY",
        "Price": price,
        "Action": action,
        "Confidence": confidence,
        "Entry Window": setup_time,
        "Entry": entry,
        "Stop Loss": sl,
        "Target": target,
        "RR": rr
    })

df = pd.DataFrame(results)

if len(df) == 0:
    st.warning("No confirmed BUY/SELL setup found right now.")
    st.stop()

df = df.sort_values(
    by=["Confidence"],
    ascending=False
)

buy_count = len(df[df["Action"] == "BUY"])
sell_count = len(df[df["Action"] == "SELL"])

top_stock = df.iloc[0]["Stock"]
top_conf = df.iloc[0]["Confidence"]

col1, col2, col3, col4 = st.columns(4)

col1.metric("BUY Signals", buy_count)
col2.metric("SELL Signals", sell_count)
col3.metric("Top Stock", top_stock)
col4.metric("Top Confidence", top_conf)

buy_df = df[df["Action"] == "BUY"].head(3)
sell_df = df[df["Action"] == "SELL"].head(3)

st.subheader("🟢 BUY SETUPS")
st.dataframe(buy_df, use_container_width=True)

st.subheader("🔴 SELL SETUPS")
st.dataframe(sell_df, use_container_width=True)