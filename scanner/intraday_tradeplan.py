import yfinance as yf
from datetime import timedelta


def get_intraday_tradeplan(symbol, action):

    try:
        data = yf.download(
            symbol,
            period="5d",
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 30:
            return None, None, None, None, "WAIT"

        close = data["Close"].squeeze()
        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        volume = data["Volume"].squeeze()

        ema20 = close.ewm(span=20).mean()
        avg_volume = volume.rolling(20).mean()

        signal_index = None

        for i in range(25, len(data)):

            if action == "BUY":
                if close.iloc[i] > ema20.iloc[i] and volume.iloc[i] > avg_volume.iloc[i]:
                    signal_index = i

            elif action == "SELL":
                if close.iloc[i] < ema20.iloc[i] and volume.iloc[i] > avg_volume.iloc[i]:
                    signal_index = i

        if signal_index is None:
            return None, None, None, None, "WAIT"

        entry = round(float(close.iloc[signal_index]), 2)

        recent_high = round(float(high.iloc[max(0, signal_index-5):signal_index+1].max()), 2)
        recent_low = round(float(low.iloc[max(0, signal_index-5):signal_index+1].min()), 2)

        candle_time = data.index[signal_index]
        start_time = candle_time.strftime("%H:%M")
        end_time = (candle_time + timedelta(minutes=15)).strftime("%H:%M")

        entry_window = f"{start_time}-{end_time}"

        if action == "BUY":

            sl = recent_low
            risk = entry - sl

            if risk <= 0:
                return None, None, None, None, "WAIT"

            target = round(entry + (risk * 2), 2)

        elif action == "SELL":

            sl = recent_high
            risk = sl - entry

            if risk <= 0:
                return None, None, None, None, "WAIT"

            target = round(entry - (risk * 2), 2)

        else:
            return None, None, None, None, "WAIT"

        return entry, sl, target, "1:2", entry_window

    except:
        return None, None, None, None, "WAIT"