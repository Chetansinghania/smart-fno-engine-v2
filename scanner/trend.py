import yfinance as yf

def get_trend(symbol):

    try:

        data = yf.download(
            symbol,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 50:
            return "NO DATA"

        # Convert DataFrame to Series
        close = data["Close"].squeeze()

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        last_close = close.iloc[-1]
        last_ema20 = ema20.iloc[-1]
        last_ema50 = ema50.iloc[-1]

        if last_close > last_ema20 and last_ema20 > last_ema50:
            return "BUY"

        elif last_close < last_ema20 and last_ema20 < last_ema50:
            return "SELL"

        else:
            return "SIDEWAYS"

    except Exception as e:
        return str(e)