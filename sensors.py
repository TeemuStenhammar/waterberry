import board
import busio
import logger
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

SENSOR_COUNT = 4
SENSOR_PINS = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]
SENSOR_MAX = 21550

def get_value(sensor):
    if sensor < 0 or sensor >= len(SENSOR_PINS):
        logger.log(f"Invalid sensor index used: {sensor}")
        return

    channel = AnalogIn(ads, SENSOR_PINS[sensor])
    percentage = channel.value / SENSOR_MAX

    return percentage * 100
