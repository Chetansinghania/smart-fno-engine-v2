import streamlit as st
import pandas as pd

from scanner.universe import load_stocks, get_stock_price
from scanner.recommendation import get_recommendation
from scanner.intraday_tradeplan import get_intraday_tradeplan

st.set_page_config(
    page_title="SMART F&O ENGINE V3",
    layout="wide"
)

st.title("SMART F&O ENGINE V3")

if st.button("🔄 Refresh Scanner"):
    st.cache_data.clear()
    st.rerun()


@st.cache_data(ttl=300)
def cached_price(stock):
    return get_stock_price(stock)


@st.cache_data(ttl=300)
def cached_recommendation(stock):
    return get_recommendation(stock)


@st.cache_data(ttl=300)
def cached_tradeplan(stock, action):
    return get_intraday_tradeplan(stock, action)


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

    entry, sl, target, rr, setup_time = cached_tradeplan(stock, action)

    if setup_time == "WAIT":
        continue

    if entry is None or sl is None or target is None:
        continue

    results.append({
        "Stock": stock,
        "Action": action,
        "Entry Time": setup_time,
        "Entry": entry,
        "SL": sl,
        "Target": target,
        "RR": rr
    })

df = pd.DataFrame(results)

if len(df) == 0:
    st.warning("No strong intraday setup found right now.")
    st.stop()

buy_df = df[df["Action"] == "BUY"].head(5)
sell_df = df[df["Action"] == "SELL"].head(5)

col1, col2 = st.columns(2)

col1.metric("BUY Setups", len(buy_df))
col2.metric("SELL Setups", len(sell_df))

st.subheader("🟢 TOP BUY SETUPS")
st.dataframe(buy_df, use_container_width=True)

st.subheader("🔴 TOP SELL SETUPS")
st.dataframe(sell_df, use_container_width=True)