import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, time
from scanner.volatility import get_daily_volatility

LOCK_FILE = os.path.join(os.path.dirname(__file__), "locked_signals.csv")


def load_locked_signals():
    if os.path.exists(LOCK_FILE):
        return pd.read_csv(LOCK_FILE)

    return pd.DataFrame(columns=[
        "date", "symbol", "action", "entry", "sl", "target",
        "risk_reward", "setup_time", "rolv"
    ])


def get_locked_signal(symbol):
    today = datetime.now().strftime("%Y-%m-%d")
    locked = load_locked_signals()

    row = locked[
        (locked["date"] == today) &
        (locked["symbol"] == symbol)
    ]

    if not row.empty:
        row = row.iloc[0]
        return (
            row["entry"],
            row["sl"],
            row["target"],
            row["risk_reward"],
            row["setup_time"],
            row.get("rolv", 0)
        )

    return None


def save_locked_signal(symbol, action, entry, sl, target, risk_reward, setup_time, rolv):
    today = datetime.now().strftime("%Y-%m-%d")
    locked = load_locked_signals()

    new_row = {
        "date": today,
        "symbol": symbol,
        "action": action,
        "entry": entry,
        "sl": sl,
        "target": target,
        "risk_reward": risk_reward,
        "setup_time": setup_time,
        "rolv": rolv
    }

    locked = pd.concat([locked, pd.DataFrame([new_row])], ignore_index=True)
    locked.to_csv(LOCK_FILE, index=False)

    return entry, sl, target, risk_reward, setup_time, rolv


def calculate_daily_vwap(data, high, low, close, volume):
    typical_price = (high + low + close) / 3
    date_group = data.index.date

    vwap = (
        (typical_price * volume).groupby(date_group).cumsum()
        / volume.groupby(date_group).cumsum()
    )

    return vwap


def get_intraday_tradeplan(symbol, action):

    try:
        locked_signal = get_locked_signal(symbol)

        if locked_signal is not None:
            return locked_signal

        data = yf.download(
            symbol,
            period="5d",
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 30:
            return None, None, None, None, "WAIT", 0

        data = data.dropna()

        close = data["Close"].squeeze()
        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        volume = data["Volume"].squeeze()

        ema20 = close.ewm(span=20).mean()
        avg_volume = volume.rolling(20).mean()

        vwap = calculate_daily_vwap(data, high, low, close, volume)

        signal_index = None
        signal_rolv = 0

        for i in range(25, len(data)):

            candle_time = data.index[i].time()

            if candle_time < time(9, 45):
                continue

            if candle_time > time(12, 30):
                continue

            if pd.isna(avg_volume.iloc[i]) or avg_volume.iloc[i] == 0:
                continue

            rvol = float(volume.iloc[i] / avg_volume.iloc[i])

            if action == "BUY":
                if (
                    close.iloc[i] > ema20.iloc[i]
                    and close.iloc[i] <= ema20.iloc[i] * 1.02
                    and close.iloc[i] > vwap.iloc[i]
                    and rvol >= 1.3
                ):
                    signal_index = i
                    signal_rolv = round(rvol, 2)
                    break

            elif action == "SELL":
                if (
                    close.iloc[i] < ema20.iloc[i]
                    and close.iloc[i] >= ema20.iloc[i] * 0.98
                    and close.iloc[i] < vwap.iloc[i]
                    and rvol >= 1.3
                ):
                    signal_index = i
                    signal_rolv = round(rvol, 2)
                    break

        if signal_index is None:
            return None, None, None, None, "WAIT", 0

        entry = round(float(close.iloc[signal_index]), 2)

        daily_volatility = get_daily_volatility(symbol)

        target_pct = daily_volatility * 0.30
        sl_pct = daily_volatility * 0.15

        if action == "BUY":
            sl = round(entry * (1 - sl_pct / 100), 2)
            target = round(entry * (1 + target_pct / 100), 2)

        elif action == "SELL":
            sl = round(entry * (1 + sl_pct / 100), 2)
            target = round(entry * (1 - target_pct / 100), 2)

        else:
            return None, None, None, None, "WAIT", 0

        candle_time = data.index[signal_index]
        setup_time = f"{candle_time.strftime('%H:%M')}-{(candle_time + timedelta(minutes=15)).strftime('%H:%M')}"

        return save_locked_signal(
            symbol,
            action,
            entry,
            sl,
            target,
            "1:2",
            setup_time,
            signal_rolv
        )

    except Exception as e:
        print("Tradeplan error:", symbol, e)
        return None, None, None, None, "WAIT", 0