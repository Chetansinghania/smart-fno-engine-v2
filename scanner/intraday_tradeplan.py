import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

LOCK_FILE = os.path.join(os.path.dirname(__file__), "locked_signals.csv")

BUFFER = 0.0005
MIN_ROLV = 1.8
VWAP_DISTANCE = 0.0015
MAX_CANDLE_RANGE_MULTIPLIER = 1.5


def load_locked_signals():
    if os.path.exists(LOCK_FILE):
        return pd.read_csv(LOCK_FILE)

    return pd.DataFrame(columns=[
        "date", "symbol", "action", "entry", "sl",
        "target1", "target2", "risk_reward", "setup_time", "rolv"
    ])


def get_locked_signal(symbol):
    today = datetime.now().strftime("%Y-%m-%d")
    locked = load_locked_signals()

    row = locked[(locked["date"] == today) & (locked["symbol"] == symbol)]

    if not row.empty:
        row = row.iloc[0]
        return (
            row["entry"], row["sl"], row["target1"], row["target2"],
            row["risk_reward"], row["setup_time"], row.get("rolv", 0)
        )

    return None


def save_locked_signal(symbol, action, entry, sl, target1, target2, risk_reward, setup_time, rolv):
    today = datetime.now().strftime("%Y-%m-%d")
    locked = load_locked_signals()

    new_row = {
        "date": today,
        "symbol": symbol,
        "action": action,
        "entry": entry,
        "sl": sl,
        "target1": target1,
        "target2": target2,
        "risk_reward": risk_reward,
        "setup_time": setup_time,
        "rolv": rolv
    }

    locked = pd.concat([locked, pd.DataFrame([new_row])], ignore_index=True)
    locked.to_csv(LOCK_FILE, index=False)

    return entry, sl, target1, target2, risk_reward, setup_time, rolv


def calculate_daily_vwap(data, high, low, close, volume):
    typical_price = (high + low + close) / 3
    date_group = data.index.date

    return (
        (typical_price * volume).groupby(date_group).cumsum()
        / volume.groupby(date_group).cumsum()
    )


def get_nifty_bias():
    try:
        data = yf.download(
            "^NSEI",
            period="5d",
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 30:
            return "NEUTRAL"

        data = data.dropna()

        close = data["Close"].squeeze()
        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        volume = data["Volume"].squeeze()

        vwap = calculate_daily_vwap(data, high, low, close, volume)

        if float(close.iloc[-1]) > float(vwap.iloc[-1]):
            return "BULLISH"

        if float(close.iloc[-1]) < float(vwap.iloc[-1]):
            return "BEARISH"

        return "NEUTRAL"

    except Exception as e:
        print("Nifty bias error:", e)
        return "NEUTRAL"


def trade_already_completed(action, data, signal_index, sl, target2):
    future_data = data.iloc[signal_index + 1:]

    if future_data.empty:
        return False

    future_high = future_data["High"].squeeze()
    future_low = future_data["Low"].squeeze()

    if action == "BUY":
        return (future_high >= target2).any() or (future_low <= sl).any()

    if action == "SELL":
        return (future_low <= target2).any() or (future_high >= sl).any()

    return False


def get_intraday_tradeplan(symbol, action, cmp_price):
    try:
        locked_signal = get_locked_signal(symbol)

        if locked_signal is not None:
            return locked_signal

        nifty_bias = get_nifty_bias()

        if action == "BUY" and nifty_bias != "BULLISH":
            return None, None, None, None, None, "WAIT", 0

        if action == "SELL" and nifty_bias != "BEARISH":
            return None, None, None, None, None, "WAIT", 0

        data = yf.download(
            symbol,
            period="5d",
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 30:
            return None, None, None, None, None, "WAIT", 0

        data = data.dropna()

        close = data["Close"].squeeze()
        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        volume = data["Volume"].squeeze()

        ema20 = close.ewm(span=20).mean()
        avg_volume = volume.rolling(20).mean()
        vwap = calculate_daily_vwap(data, high, low, close, volume)

        candle_range = high - low
        avg_candle_range = candle_range.rolling(20).mean()

        today = pd.Timestamp.now(tz="Asia/Kolkata").date()
        today_mask = data.index.date == today

        best_index = None
        best_rolv = 0

        for i in range(25, len(data)):

            if not today_mask[i]:
                continue

            if pd.isna(avg_volume.iloc[i]) or avg_volume.iloc[i] == 0:
                continue

            if pd.isna(avg_candle_range.iloc[i]) or avg_candle_range.iloc[i] == 0:
                continue

            current_range = float(candle_range.iloc[i])
            average_range = float(avg_candle_range.iloc[i])

            if current_range > average_range * MAX_CANDLE_RANGE_MULTIPLIER:
                continue

            rvol = float(volume.iloc[i] / avg_volume.iloc[i])

            if action == "BUY":
                signal_found = (
                    close.iloc[i] > ema20.iloc[i]
                    and ema20.iloc[i] > ema20.iloc[i - 1]
                    and close.iloc[i] > vwap.iloc[i]
                    and ((close.iloc[i] - vwap.iloc[i]) / vwap.iloc[i]) >= VWAP_DISTANCE
                    and rvol >= MIN_ROLV
                )

            elif action == "SELL":
                signal_found = (
                    close.iloc[i] < ema20.iloc[i]
                    and ema20.iloc[i] < ema20.iloc[i - 1]
                    and close.iloc[i] < vwap.iloc[i]
                    and ((vwap.iloc[i] - close.iloc[i]) / vwap.iloc[i]) >= VWAP_DISTANCE
                    and rvol >= MIN_ROLV
                )

            else:
                signal_found = False

            if signal_found and rvol > best_rolv:
                best_index = i
                best_rolv = rvol

        if best_index is None:
            return None, None, None, None, None, "WAIT", 0

        signal_high = float(high.iloc[best_index])
        signal_low = float(low.iloc[best_index])

        if action == "BUY":
            entry = round(signal_high * (1 + BUFFER), 2)
            sl = round(signal_low, 2)
            risk = entry - sl
            target1 = round(entry + risk, 2)
            target2 = round(entry + (risk * 2), 2)

        elif action == "SELL":
            entry = round(signal_low * (1 - BUFFER), 2)
            sl = round(signal_high, 2)
            risk = sl - entry
            target1 = round(entry - risk, 2)
            target2 = round(entry - (risk * 2), 2)

        else:
            return None, None, None, None, None, "WAIT", 0

        if risk <= 0:
            return None, None, None, None, None, "WAIT", 0

        if trade_already_completed(action, data, best_index, sl, target2):
            return None, None, None, None, None, "WAIT", 0

        candle_time = data.index[best_index]
        setup_time = f"{candle_time.strftime('%H:%M')}-{(candle_time + timedelta(minutes=15)).strftime('%H:%M')}"

        return save_locked_signal(
            symbol,
            action,
            entry,
            sl,
            target1,
            target2,
            "1:2",
            setup_time,
            round(best_rolv, 2)
        )

    except Exception as e:
        print("Tradeplan error:", symbol, e)
        return None, None, None, None, None, "WAIT", 0