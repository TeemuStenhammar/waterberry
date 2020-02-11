import RPi.GPIO as GPIO
import time
import logger
import config

PUMP_COUNT = 4
PUMP_PINS = [4, 17, 27, 22]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def init_pump(pump_pin):
    GPIO.setup(pump_pin, GPIO.OUT)
    GPIO.output(pump_pin, GPIO.LOW)
    GPIO.output(pump_pin, GPIO.HIGH)

def pump_on(pump, delay = 1):
    if pump < 0 or pump >= len(PUMP_PINS):
        logger.log(f"Invalid pump index used: {pump}")
        return

    logger.log(f"Pump {pump} watering for {delay}s")
    config.update_last_watered(pump)

    pump_pin = PUMP_PINS[pump]
    init_pump(pump_pin)
    GPIO.output(pump_pin, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(pump_pin, GPIO.HIGH)

def pumps_on(pumps, delay = 1):
    for p in pumps:
        if p < 0 or p >= len(PUMP_PINS):
            continue

        config.update_last_watered(p)
        pump_pin = PUMP_PINS[p]
        init_pump(pump_pin)
        GPIO.output(pump_pin, GPIO.LOW)

    time.sleep(delay)

    for p in pumps:
        if p < 0 or p >= len(PUMP_PINS):
            continue

        pump_pin = PUMP_PINS[p]
        GPIO.output(pump_pin, GPIO.HIGH)

def cleanup():
    for pin in PUMP_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
