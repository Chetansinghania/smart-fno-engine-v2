import yfinance as yf

def get_trend(symbol):

    try:

        data = yf.download(
            symbol,
            period="3mo",
            interval="1d",
            progress=False
        )

        ema20 = data["Close"].ewm(span=20).mean()

        latest_close = data["Close"].iloc[-1]

        latest_ema = ema20.iloc[-1]

        if latest_close > latest_ema:
            return "BULLISH"
        else:
            return "BEARISH"

    except:
        return "NA"