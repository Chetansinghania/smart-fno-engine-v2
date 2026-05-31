import yfinance as yf

def get_tf_trend(symbol, interval):

    try:

        data = yf.download(
            symbol,
            period="6mo",
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if len(data) < 50:
            return "NO DATA"

        close = data["Close"].squeeze()

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        close_last = close.iloc[-1]
        ema20_last = ema20.iloc[-1]
        ema50_last = ema50.iloc[-1]

        if close_last > ema20_last and ema20_last > ema50_last:
            return "BUY"

        elif close_last < ema20_last and ema20_last < ema50_last:
            return "SELL"

        else:
            return "SIDEWAYS"

    except:
        return "ERROR"