import sys
import getopt
import time
import logger
import pumps

def main(argv):
    logger.log("Starting autowatering!!")
    try:
        opts, args = getopt.getopt(argv, "d:t:", ["delay=", "duration="])
    except getopts.GetoptError:
        logger.log("Auto watering failed with invalid arguments")
        sys.exit(2)

    delay = -1
    duration = -1
    pump_list = list()

    for o, a in opts:
        if o in ("-d", "--delay"):
            delay = int(a)
        elif o in ("-t", "--duration"):
            duration = int(a)

    for a in args:
        pump_list.append(int(a))

    if delay < 0 or duration < 0:
        logger.log("Either duration or delay is missing from auto watering arguments")
        sys.exit(1)

    if len(pump_list) == 0:
        print("No pumps specified, exiting...")
        sys.exit(0)

    auto_water(delay, duration, pump_list)

def auto_water(delay, duration, pump_list):
    logger.log(f"Starting auto watering with delay {delay}s and duration {duration}s")
    logger.log(f"Pumps: {pump_list}")

    try:
        while True:
            time.sleep(delay)
            pumps.pumps_on(pump_list, duration)
    except KeyboardInterrupt:
        pumps.cleanup()

if __name__ == "__main__":
    main(sys.argv[1:])
