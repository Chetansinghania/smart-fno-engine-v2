import yfinance as yf


def get_trend(symbol):

    try:
        data = yf.download(
            symbol,
            period="3mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 25:
            return "NO DATA"

        close = data["Close"].squeeze()

        ema20 = close.ewm(span=20).mean()

        last_close = close.iloc[-1]
        last_ema20 = ema20.iloc[-1]

        if last_close > last_ema20:
            return "BUY"

        elif last_close < last_ema20:
            return "SELL"

        else:
            return "SIDEWAYS"

    except Exception as e:
        return str(e)