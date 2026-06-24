import streamlit as st
import pandas as pd

from scanner.universe import load_stocks, get_stock_price
from scanner.recommendation import get_recommendation
from scanner.intraday_tradeplan import get_intraday_tradeplan

st.set_page_config(
    page_title="SMART F&O ENGINE V5.3",
    layout="wide"
)

st.title("SMART F&O ENGINE V5.3 - TOP 3 TRADES")

if st.button("Refresh Scanner"):
    st.cache_data.clear()
    st.rerun()


@st.cache_data(ttl=300)
def cached_price(stock):
    return get_stock_price(stock)


@st.cache_data(ttl=300)
def cached_recommendation(stock):
    return get_recommendation(stock)


@st.cache_data(ttl=300)
def cached_tradeplan(stock, action, price):
    return get_intraday_tradeplan(stock, action, price)


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

    entry, sl, target1, target2, rr, setup_time, rolv = cached_tradeplan(stock, action, price)

    if setup_time == "WAIT":
        continue

    if entry is None or sl is None or target1 is None or target2 is None:
        continue

    results.append({
        "Stock": stock,
        "Action": action,
        "CMP": round(price, 2),
        "ROLV": rolv,
        "Entry": entry,
        "SL": sl,
        "Target 1": target1,
        "Target 2": target2,
        "RR": rr
    })


df = pd.DataFrame(results)

if len(df) == 0:
    st.warning("No active trade setup found right now.")
    st.stop()


buy_count = len(df[df["Action"] == "BUY"])
sell_count = len(df[df["Action"] == "SELL"])

st.subheader("Signal Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Active Signals", len(df))
col2.metric("BUY Signals", buy_count)
col3.metric("SELL Signals", sell_count)


ranked_df = df.sort_values(
    by="ROLV",
    ascending=False
).head(3)


st.subheader("TOP 3 TRADES")

st.success("Top 3 trades ranked by ROLV. Book 50% at Target 1 and trail rest to Target 2.")

st.dataframe(
    ranked_df,
    use_container_width=True
)


st.subheader("Trading Rule")

st.info(
    "Trade only one at a time. "
    "Book 50% quantity at Target 1. "
    "After Target 1, move SL to entry price. "
    "Hold remaining 50% for Target 2. "
    "Maximum 2 trades per day."
)


with st.expander("Show All Active Scanner Signals"):
    st.dataframe(
        df.sort_values(by="ROLV", ascending=False),
        use_container_width=True
    )