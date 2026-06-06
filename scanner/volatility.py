import yfinance as yf


def get_daily_volatility(symbol):

    try:
        data = yf.download(
            symbol,
            period="30d",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if len(data) < 20:
            return 2.0

        high = data["High"].squeeze()
        low = data["Low"].squeeze()
        close = data["Close"].squeeze()

        daily_range_pct = ((high - low) / close) * 100

        avg_volatility = daily_range_pct.tail(20).mean()

        return round(float(avg_volatility), 2)

    except:
        return 2.0