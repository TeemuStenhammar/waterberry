import os
import datetime
import logger
import json
from typing import List

MY_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(MY_PATH, f"{CONFIG_DIR}/automation_config.json")
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
TIME_FORMAT = "%H:%M"

os.makedirs(os.path.join(MY_PATH, CONFIG_DIR), exist_ok = True)

class TimeBasedWatering:
    def __init__(self, pump, delay, when):
        self.pump = pump
        self.delay = delay
        self.when = when

class AutomationConfig:
    def __init__(self):
        self.timed = list()
        self.drip = list()
        self.drip_duration = 1
        self.drip_delay = 1

def update_last_watered(pump):
    path = os.path.join(MY_PATH, f"{CONFIG_DIR}/last_watered_{pump}.txt")
    f = open(path, "w")
    f.write("{}".format(datetime.datetime.now()))
    f.close()

def get_last_watered(pump):
    path = os.path.join(MY_PATH, f"{CONFIG_DIR}/last_watered_{pump}.txt")
    if os.path.exists(path):
        try:
            f = open(path, "r")
            date_str = f.read().strip()
            f.close()
            return date_str
        except:
            return "never"
    return "never"

def time_since_watered(pump):
    path = os.path.join(MY_PATH, f"{CONFIG_DIR}/last_watered_{pump}.txt")
    dt = datetime.datetime.min
    if os.path.exists(path):
        try:
            f = open(path, "r")
            date_str = f.read()
            f.close()
            dt = datetime.datetime.strptime(date_str, DATE_FORMAT)
        except:
            logger.log("Error while reading last watered for {pump}: Could not parse content")
    else:
        logger.log(f"Error while getting time since watered for {pump}: File does not exist")

    difference = datetime.datetime.now() - dt
    return difference

def as_automation_config(dict):
    if "timed" in dict:
        config = AutomationConfig()
        for t in dict["timed"]:
            config.timed.append(t)
        for d in dict["drip"]:
            config.drip.append(d)
        config.drip_duration = dict["drip_duration"]
        config.drip_delay = dict["drip_delay"]
        return config
    if "pump" in dict:
        pump = dict["pump"]
        delay = dict["delay"]
        when = datetime.datetime.strptime(dict["when"], TIME_FORMAT).time()
        return TimeBasedWatering(pump, delay, when)

def load_automation_config():
    if os.path.exists(CONFIG_FILE):
        try:
            f = open(CONFIG_FILE, "r")
            str = f.read()
            return json.loads(str, object_hook = as_automation_config)
        except:
            print("Contents was not json, recreating the file")

    return AutomationConfig()

automation_config = load_automation_config()

def json_converter(o):
    if isinstance(o, datetime.datetime):
        return "{}".format(o)
    if isinstance(o, TimeBasedWatering):
        return {
            "pump": o.pump,
            "delay": o.delay,
            "when": o.when.strftime(TIME_FORMAT)
        }
    else:
        print(f"Type not supported: {type(o)}")

def store_automation_config(config: AutomationConfig):
    f = open(CONFIG_FILE, "w")
    f.write(json.dumps(config.__dict__, default = json_converter))
    f.close()

def add_time_based_watering(pump: int, delay: int, when: datetime.time):
    automation = TimeBasedWatering(pump, delay, when)
    automation_config.timed.append(automation)
    store_automation_config(automation_config)

def update_time_based_watering(id: int, pump: int, delay: int, when: datetime.time):
    if id >= 0 and id < len(automation_config.timed):
        automation_config.timed[id].pump = pump
        automation_config.timed[id].delay = delay
        automation_config.timed[id].when = when
        store_automation_config(automation_config)

def delete_time_based_watering(id: int):
    if id >= 0 and id < len(automation_config.timed):
        del automation_config.timed[id]
        store_automation_config(automation_config)

def get_time_based_waterings():
    return automation_config.timed

def set_drip_enabled(pump: int, enabled: bool):
    if enabled and pump not in automation_config.drip:
        automation_config.drip.append(pump)
    if not enabled and pump in automation_config.drip:
        automation_config.drip.remove(pump)
    store_automation_config(automation_config)

def get_drip_waterings():
    return automation_config.drip

def set_drip_delay(delay: int):
    automation_config.drip_delay = delay
    store_automation_config(automation_config)

def get_drip_delay():
    return automation_config.drip_delay

def set_drip_duration(duration: int):
    automation_config.drip_duration = duration
    store_automation_config(automation_config)

def get_drip_duration():
    return automation_config.drip_duration

def print_current_config():
    print(json.dumps(
        automation_config.__dict__,
        default = json_converter,
        sort_keys = True,
        indent = 4
    ))
