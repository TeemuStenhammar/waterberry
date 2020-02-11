import config
import datetime
import pumps
import os

def pump_is_dripping(pump: int):
    return pump in config.get_drip_waterings()

def time_is_due(time):
    now = datetime.datetime.now().time()
    return now > time

def already_watered(pump, time):
    last_watered_str = config.get_last_watered(pump)

    # Special case of not having value at all
    if last_watered_str == "never":
        return False

    last_watered = datetime.datetime.strptime(last_watered_str, config.DATE_FORMAT)
    last_watered_date = last_watered.date()
    last_watered_time = last_watered.time()
    now = datetime.datetime.now()

    # If last water is not today
    if last_watered_date < now.date():
        return False

    return last_watered_time > time

def check_timed():
    for timed in config.get_time_based_waterings():
        if pump_is_dripping(timed.pump):
            print("is dripping, won't water")
            continue
        if not time_is_due(timed.when):
            print("time is not due yet")
            continue
        if already_watered(timed.pump, timed.when):
            print("already watered")
            continue

        # This pump should water now
        pumps.pump_on(timed.pump, timed.delay)

if __name__ == "__main__":
    check_timed()
