from scanner.scoring import get_score
from scanner.trend import get_trend
from datetime import datetime, time


def get_entry_window():

    now = datetime.now().time()

    market_windows = [
        ("9:30-9:45", time(9, 30), time(9, 45)),
        ("9:45-10:00", time(9, 45), time(10, 0)),
        ("10:00-10:15", time(10, 0), time(10, 15)),
        ("10:15-10:30", time(10, 15), time(10, 30)),
        ("10:30-10:45", time(10, 30), time(10, 45)),
        ("10:45-11:00", time(10, 45), time(11, 0)),
        ("11:00-11:15", time(11, 0), time(11, 15)),
        ("11:15-11:30", time(11, 15), time(11, 30)),
        ("11:30-11:45", time(11, 30), time(11, 45)),
        ("11:45-12:00", time(11, 45), time(12, 0)),
        ("12:00-12:15", time(12, 0), time(12, 15)),
        ("12:15-12:30", time(12, 15), time(12, 30)),
        ("12:30-12:45", time(12, 30), time(12, 45)),
        ("12:45-13:00", time(12, 45), time(13, 0)),
        ("13:00-13:15", time(13, 0), time(13, 15)),
        ("13:15-13:30", time(13, 15), time(13, 30)),
        ("13:30-13:45", time(13, 30), time(13, 45)),
        ("13:45-14:00", time(13, 45), time(14, 0)),
        ("14:00-14:15", time(14, 0), time(14, 15)),
        ("14:15-14:30", time(14, 15), time(14, 30)),
        ("14:30-14:45", time(14, 30), time(14, 45)),
        ("14:45-15:00", time(14, 45), time(15, 0)),
    ]

    for label, start, end in market_windows:
        if start <= now < end:
            return label

    if now < time(9, 30):
        return "9:30-9:45"

    return "Market closed"


def get_recommendation(symbol):

    daily_trend = get_trend(symbol)
    entry_window = get_entry_window()

    if daily_trend == "BUY":
        score = get_score(symbol, "BUY")
        return "BUY", score, entry_window

    elif daily_trend == "SELL":
        score = get_score(symbol, "SELL")
        return "SELL", score, entry_window

    else:
        return "NO TRADE", 40, "-"