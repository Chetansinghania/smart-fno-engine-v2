import yfinance as yf


def get_score(symbol, action):

    try:
        data = yf.download(
            symbol,
            period="3mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 30:
            return 40

        close = data["Close"].squeeze()
        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        volume = data["Volume"].squeeze()

        daily_range = high - low
        avg_range = daily_range.tail(20).mean()
        today_range = daily_range.iloc[-1]

        atr_score = 15 if today_range > avg_range else 0

        avg_volume = volume.tail(20).mean()
        today_volume = volume.iloc[-1]

        volume_score = 15 if today_volume > avg_volume else 0

        latest_close = close.iloc[-1]
        avg_close_20 = close.tail(20).mean()

        momentum_score = 0

        if action == "BUY" and latest_close > avg_close_20:
            momentum_score = 20

        elif action == "SELL" and latest_close < avg_close_20:
            momentum_score = 20

        base_score = 40

        final_score = base_score + atr_score + volume_score + momentum_score

        return min(final_score, 100)

    except:
        return 40