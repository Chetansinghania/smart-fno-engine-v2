import pandas as pd
import yfinance as yf

def load_stocks():

    df = pd.read_excel("data/fno_stocks.xlsx")

    return df["SYMBOL"].tolist()

def get_stock_price(symbol):

    try:

        stock = yf.Ticker(symbol)

        data = stock.history(period="5d")

        if len(data) == 0:
            return None

        return round(data["Close"].iloc[-1], 2)

    except:
        return None