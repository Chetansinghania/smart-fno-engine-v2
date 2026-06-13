import yfinance as yf
import pandas as pd
from datetime import time


def calculate_daily_vwap(data, high, low, close, volume):
    typical_price = (high + low + close) / 3
    date_group = data.index.date

    vwap = (
        (typical_price * volume).groupby(date_group).cumsum()
        / volume.groupby(date_group).cumsum()
    )

    return vwap


def get_score(symbol, action):
    try:
        data = yf.download(
            symbol,
            period="5d",
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 30:
            return 0

        data = data.dropna()

        close = data["Close"].squeeze()
        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        volume = data["Volume"].squeeze()

        ema20 = close.ewm(span=20).mean()
        avg_volume = volume.rolling(20).mean()
        vwap = calculate_daily_vwap(data, high, low, close, volume)

        best_score = 0

        for i in range(25, len(data)):

            candle_time = data.index[i].time()

            if candle_time < time(9, 45):
                continue

            if candle_time > time(12, 30):
                continue

            if pd.isna(avg_volume.iloc[i]) or avg_volume.iloc[i] == 0:
                continue

            price = float(close.iloc[i])
            ema = float(ema20.iloc[i])
            vw = float(vwap.iloc[i])
            rvol = float(volume.iloc[i] / avg_volume.iloc[i])

            score = 0

            if action == "BUY":
                if price > ema:
                    score += 25

                if price > vw:
                    score += 25

                if price <= ema * 1.02:
                    score += 15

                if rvol >= 1.3:
                    score += min(rvol * 20, 35)

            elif action == "SELL":
                if price < ema:
                    score += 25

                if price < vw:
                    score += 25

                if price >= ema * 0.98:
                    score += 15

                if rvol >= 1.3:
                    score += min(rvol * 20, 35)

            best_score = max(best_score, score)

        return round(best_score, 2)

    except Exception as e:
        print("Scoring error:", symbol, e)
        return 0