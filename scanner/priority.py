from datetime import time


def get_priority(setup_time):

    try:

        start_time = setup_time.split("-")[0]

        hour = int(start_time.split(":")[0])
        minute = int(start_time.split(":")[1])

        t = time(hour, minute)

        if t < time(11, 30):
            return "HIGH"

        elif t < time(14, 0):
            return "NORMAL"

        else:
            return "LOW"

    except:
        return "-"