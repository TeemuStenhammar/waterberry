from flask import Flask, render_template, request, redirect, url_for
import psutil
import datetime
import os
import config
import logger
import pumps
import sensors

app = Flask(__name__)

class DripState:
    def __init__(self, pump, state):
        self.pump = pump
        self.state = state

class TimedEditState:
    def __init__(self, id, pump, delay, when):
        self.id = id
        self.pump = pump
        self.delay = delay
        self.when = when

class State:
    def __init__(self):
        self.logdate = datetime.date.today()
        self.pumps = range(pumps.PUMP_COUNT)
        self.sensors = range(sensors.SENSOR_COUNT)
        self.timed = config.get_time_based_waterings()
        self.drip = config.get_drip_waterings()
        self.drip_delay = config.get_drip_delay()
        self.drip_duration = config.get_drip_duration()
        self.timed_edit = None
        self.drip_edit = False
        self.water_now_pump = 0
        self.water_now_duration = 10

state = State()

def template(title = "HELLO!", text = "", error = ""):
    now = datetime.datetime.now()
    timeString = now

    drip_states = list()
    last_watered = list()
    for p in state.pumps:
        drip_states.append(DripState(p, p in state.drip))
        last_watered.append(config.get_last_watered(p))

    sensor_states = list()
    for s in state.sensors:
        sensor_states.append(sensors.get_value(s))

    templateDate = {
        'title' : title,
        'time' : timeString,
        'text' : text,
        'error' : error,
        'logdate': state.logdate,
        'logs' : logger.get_logs(state.logdate).splitlines(),
        'drips' : drip_states,
        'drip_delay' : state.drip_delay,
        'drip_duration' : state.drip_duration,
        'sensors' : sensor_states,
        'timed' : state.timed,
        'timed_edit' : state.timed_edit,
        'drip_edit' : state.drip_edit,
        'last_watered' : last_watered,
        'water_now_pump' : state.water_now_pump,
        'water_now_duration' : state.water_now_duration
    }
    return templateDate

@app.route("/")
def hello():
    templateData = template()
    return render_template('main.html', **templateData)

@app.route("/sensor")
def action():
    templateData = template()
    return render_template('main.html', **templateData)

@app.route("/water", methods=["POST"])
def water_now():
    pump = request.form["pump"]
    duration = request.form["duration"]
    if pump == "" or duration == "":
        templateData = template(error = "All fields are required when watering!")
        return render_template("main.html", **templateData)

    state.water_now_pump = int(pump)
    state.water_now_duration = int(duration)

    pumps.pump_on(state.water_now_pump, state.water_now_duration)
    templateData = template()
    return render_template('main.html', **templateData)

def launch_drip_watering():
    logger.log("Launching drip watering")

    path = os.path.abspath(os.path.dirname(__file__))
    script = os.path.join(path, "auto_water.py")

    # Figure out if a drip watering script is already running
    alreadyRunning = False
    for process in psutil.process_iter():
        try:
            if process.cmdline()[1] == script:
                alreadyRunning = True
        except:
            pass

    # Figure if there are drip waterings to run
    shouldRun = len(state.drip) > 0

    if not shouldRun and alreadyRunning:
        logger.log("Should not run, but was found running -> killing it")
        os.system(f"pkill -f {script}")
        pumps.cleanup()
        return

    if shouldRun and alreadyRunning:
        logger.log("Should run, so killing earlier running instance")
        os.system(f"pkill -f {script}")
        pumps.cleanup()

    if shouldRun:
        logger.log("Starting up the script!")
        path = os.path.abspath(os.path.dirname(__file__))
        script = os.path.join(path, "auto_water.py")
        command = f"python3 {script} -d {state.drip_delay} -t {state.drip_duration}"
        for p in state.drip:
            command += f" {p}"
        command += "&"
        os.system(command)
        logger.log("Script should be running now")
    logger.log("Exiting the launch method")

@app.route("/auto/drip/<int:id>/<toggle>")
def drip_water(id, toggle):
    if toggle == "ON":
        config.set_drip_enabled(id, True)
    else:
        config.set_drip_enabled(id, False)

    state.drip = config.get_drip_waterings()

    launch_drip_watering()
    templateData = template(text = "")
    return render_template('main.html', **templateData)

@app.route("/auto/drip/edit")
def drip_water_edit():
    state.drip_edit = True
    templateData = template(text = "")
    return render_template('main.html', **templateData)

@app.route("/auto/drip/config", methods=["POST"])
def drip_water_config():
    if request.form["submit"] == "save":
        delay = request.form["delay"]
        duration = request.form["duration"]
        if delay == "" or duration == "":
            templateData = template(error = "All fields are required when setting drip configuration!")
            return render_template("main.html", **templateData)

        config.set_drip_delay(int(delay))
        config.set_drip_duration(int(duration))
        state.drip_delay = config.get_drip_delay()
        state.drip_duration = config.get_drip_duration()
        launch_drip_watering()

    state.drip_edit = False
    templateData = template(text = "")
    return render_template('main.html', **templateData)

@app.route("/auto/timebased/create")
def create_time_based():
    config.add_time_based_watering(1, 1, datetime.datetime.now().time())
    state.timed = config.get_time_based_waterings()
    return edit_time_based(len(state.timed) - 1)

@app.route("/auto/timebased/<int:id>", methods=["POST"])
def save_time_based(id):
    if request.form["submit"] == "save":
        pump = request.form["pump"]
        delay = request.form["delay"]
        when = request.form["when"]
        if pump == "" or delay == "" or when == "":
            templateData = template(error = "All fields are required when setting time based watering!")
            return render_template("main.html", **templateData)

        config.update_time_based_watering(id, int(pump), int(delay), datetime.datetime.strptime(when, config.TIME_FORMAT).time())
        state.timed = config.get_time_based_waterings()

    state.timed_edit = None
    templateData = template(text = "")
    return render_template('main.html', **templateData)

@app.route("/auto/timebased/<int:id>/edit")
def edit_time_based(id):
    state.timed_edit = TimedEditState(
        id,
        state.timed[id].pump,
        state.timed[id].delay,
        state.timed[id].when.strftime(config.TIME_FORMAT)
    )
    templateData = template(text = "")
    return render_template('main.html', **templateData)

@app.route("/auto/timebased/<int:id>/delete")
def delete_time_based(id):
    config.delete_time_based_watering(id)
    state.timed = config.get_time_based_waterings()
    templateData = template(text = "")
    return render_template('main.html', **templateData)

@app.route("/logs/<direction>")
def update_logs(direction):
    if direction == "next":
        if state.logdate != datetime.date.today():
            state.logdate = state.logdate + datetime.timedelta(days = 1)
    else:
        state.logdate = state.logdate - datetime.timedelta(days = 1)

    templateData = template(text = "")
    return render_template('main.html', **templateData)

if __name__ == "__main__":
    # Start drip waterings, if any
    launch_drip_watering()

    app.secret_key = "secret"
    app.run(host='0.0.0.0', port=80, debug=True)
