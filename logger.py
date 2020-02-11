import os
import datetime
import logging

MY_PATH = os.path.abspath(os.path.dirname(__file__))
LOGS_DIR = os.path.join(MY_PATH, "logs")

os.makedirs(LOGS_DIR, exist_ok = True)

LOG_FORMAT = "%(asctime)s - %(message)s"
logging.basicConfig(
    filename = f"{LOGS_DIR}/{datetime.date.today()}.log",
    level = logging.INFO,
    format = LOG_FORMAT
)

logger = logging.getLogger()

def log(message):
    logger.info(message)

def get_logs(date: datetime.date):
    filename = f"{LOGS_DIR}/{date}.log"
    if os.path.exists(filename):
        f = open(filename, "r")
        logs = f.read()
        f.close()
        return logs

    return ""
