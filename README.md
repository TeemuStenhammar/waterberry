# WaterBerry
This is a hobby project for automating in-house seedling irrigation with 
Raspberry Pi 4. Currently 4 pumps and 4 soil moisture sensors are supported.    

### Features:

* Time-based watering with individual pumps 
* Drip-irrigation mode
* Simple website to configure automations

The starting point for this projects which is still visible in some source 
files is Ben Eagans hackster.io 
[post](https://www.hackster.io/ben-eagan/raspberry-pi-automated-plant-watering-with-website-8af2dc).

## Hardware
* [Raspberry Pi 4B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) 
* [5V 4 Channel Relay](https://core-electronics.com.au/5v-4-channel-relay-module-10a.html)
* [4 x SparkFun Soil Moisture Sensor](https://www.hackster.io/sparkfun/products/sparkfun-soil-moisture-sensor-with-screw-terminals1?ref=project-8af2dc)
* 4 x 3-6V Submerible Pump
* [16bit I2C 4 Channel ADS1115 Analog to Digital Module](https://www.amazon.in/Robocraze-Channel-ADS1115-Module-569/dp/B077QXWCW1)
* Flexible water line 
* Plastic pipe fittings
* Electric wiring

### Wiring

#### 4 Channel Relay

This relay will control water pumps. Any available GPIO pins can be used for pumps as 
long as those GPIO numbers are updated to the *pumps.py*.

* GND to pin 14 (GND) 
* VCC to pin 4 (5V power) 
* IN1 to pin 15 (GPIO 22) 
* IN2 to pin 13 (GPIO 27) 
* IN3 to pin 11 (GPIO 17)
* IN4 to pin 7 (GPIO 4)

#### ADS1115 Module

This module will connect all 4 soil moisture sensors via I2C to the Raspberry Pi.  

* VCC to pin 1 (3.3V power) 
* GND to pin 6 (GND) 
* SCL to pin 5 (GPIO 3 / SCL)
* SDA to pin 3 (GPIO 2 / SDA)

#### Soil moisture sensor

For these sensors I divided VCC and GND from ADS1115 so that effectively every 
sensor got VCC from pin 1 and GND from pin 6. Then the signal line is connected 
to one channel in the ADS1115.

## Prerequisites

* Raspberry Pi must have I2C enabled. This can be done in `raspi-config`. 
* The source code uses adafruits library for ADS1115 communication. 
This library can be installed with:
`sudo pip3 install adafruit-circuitpython-ads1x15`


## Running the website

Running the Flask website in Raspberry Pi while binding to port 80 cannot 
normally be done without sudo. However, running the website with sudo privileges 
is an another can of worms with problems to write and read to log files and with 
running cron jobs. So, in order to ease up this pain a bit, this 
[site](https://gist.github.com/justinmklam/f13bb53be9bb15ec182b4877c9e9958d) 
offers an easy solution to it. 

In short: use authbind:

```
sudo apt install authbind

# Configure access to port 80
sudo touch /etc/authbind/byport/80 
sudo chmod 777 /etc/authbind/byport/80
```

And then the application can be run with:
`authbind --deep python3 web_plants.py`

After this the website can be accessed from your Raspberrys port 80.


## Setting up necessary cron jobs

First cron job is needed to run the website when Raspberry Pi boots up. 
Access crontab with command `crontab -e` and add following line to it:
`@reboot authbind --deep python3 ~/waterberry/web_plants.py &` 

`@reboot` runs the task at reboot and `&` at the end runs it as a background task. 

Second cron job is to check every 5mins if there is a need to water something or not. 
Add following line to the crontab:
`*/5 * * * * python3 ~/waterberry/check_timed.py`


## Files

``` 
project 
│ README.md 
│ web_plants.py  // Website 
│ logger.py      // Logging to files 
│ pumps.py       // Pump pin management 
│ sensors.py     // Sensor pin management 
│ config.py      // Permanent storing of config 
│ auto_water.py  // Drip irrigation script 
│ check_timed.py // Checks and waters based of time 
│ 
└───logs         // All logs stored here 
│   │ yyyy-mm-dd.log 
│ 
└───config       // Permanently stored configuration
│   │ automation_config.txt 
│   │ last_watered_x.txt
│
└───templates    // HTML templates for Flask
    │ main.html  // The main template

```

## License
Waterberry is free and unencumbered public domain software. For more information, 
see [http://unlicense.org/](http://unlicense.org/) or the accompanying UNLICENSE file.
