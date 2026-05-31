import streamlit as st
import pandas as pd

from scanner.universe import load_stocks, get_stock_price
from scanner.recommendation import get_recommendation
from scanner.intraday_tradeplan import get_intraday_tradeplan
from scanner.priority import get_priority

st.set_page_config(
    page_title="SMART F&O ENGINE V2",
    layout="wide"
)

st.title("SMART F&O DECISION ENGINE V2")

stocks = load_stocks()

results = []

for stock in stocks:

    price = get_stock_price(stock)

    if price is None:
        continue

    if price < 2500:
        continue

    action, confidence, entry_window = get_recommendation(stock)

    if confidence < 75:
        continue

    entry, sl, target, rr, setup_time = get_intraday_tradeplan(stock, action)

    priority = get_priority(setup_time)

    if confidence >= 90:
        status = "READY"
    else:
        status = "WATCH"

    results.append({
        "Stock": stock,
        "Status": status,
        "Priority": priority,
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
    st.warning("No trade setups found right now.")
    st.stop()

priority_order = {
    "HIGH": 3,
    "NORMAL": 2,
    "LOW": 1
}

df["Priority Score"] = df["Priority"].map(priority_order)
df = df[df["Priority"] != "LOW"]
df = df.sort_values(
    by=["Priority Score", "Confidence"],
    ascending=False
)

df = df.drop(columns=["Priority Score"])

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