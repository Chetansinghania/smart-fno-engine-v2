import yfinance as yf


def get_trade_plan(symbol, action):

    try:

        data = yf.download(
            symbol,
            period="15d",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 5:
            return None, None, None, None

        close = data["Close"].squeeze()

        entry = round(float(close.iloc[-1]), 2)

        recent_high = round(float(data["High"].tail(5).max()), 2)
        recent_low = round(float(data["Low"].tail(5).min()), 2)

        if action == "BUY":

            sl = recent_low

            risk = entry - sl

            target = round(entry + (risk * 2), 2)

        elif action == "SELL":

            sl = recent_high

            risk = sl - entry

            target = round(entry - (risk * 2), 2)

        else:

            return None, None, None, None

        return entry, sl, target, "1:2"

    except:

        return None, None, None, None