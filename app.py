#!/usr/bin/python3
'''
Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson
Modified by Rui Santos
Complete project details: http://randomnerdtutorials.com
'''
# -----------------------------------------------------------------------------------------------------------------------------------------------------------
#    To run automatically at boot.
#    sudo nano /etc/rc.local
#    sudo python3 /home/pi/Documents/web-server/app.py &
#
#    https://randomnerdtutorials.com/raspberry-pi-web-server-using-flask-to-control-gpios/
# 
#    3/1/2019 Matthew Brown - created file
#    3/9/2019 Don Bush - added trafficLightController
#    11/2/2021 Dragan added  Adafruit_PCA9685 and board for driving servos
#    09/20/2022 Dragan added thread moveFingers 
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

import logging
import os
import time
import logger
import signal
import threading
import queue as queue
#import trafficLightController
import RPi.GPIO as GPIO

from flask import Flask, render_template, request
#from __future__ import division


# Import the PCA9685 module.
import Adafruit_PCA9685
# Uncomment to enable debug output.
#import logging
# logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()
# Configure min and max servo pulse lengths
servo_min = 250  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
# Helper function to make setting a servo pulse width simpler.

testStopEvent = threading.Event()
testStopEvent.clear()
print('START')
def moveFingers(stop_event):
    print("uso u moveFingers")
    while (True):
        GPIO.output(cPin, GPIO.LOW)  # HIGH
        pwm.set_pwm(srv, 0, servo_min)
        time.sleep(1)
        GPIO.output(cPin, GPIO.HIGH)  # LOW
        pwm.set_pwm(srv, 0, servo_max)
        time.sleep(1)
        GPIO.output(cPin, GPIO.LOW)  # HIGH
        pwm.set_pwm(srv, 0, servo_min)
        if stop_event.isSet():
            print("break moveFingers")
            break
        print("inside moveFingers")

test = threading.Thread(name = 'test', target=moveFingers, args=((testStopEvent,)))
test.daemon = True

# def set_servo_pulse(channel, pulse):
#     pulse_length = 1000000    # 1,000,000 us per second
#     pulse_length //= 60       # 60 Hz
#     print('{0}us per period'.format(pulse_length))
#     pulse_length //= 4096     # 12 bits of resolution
#     print('{0}us per bit'.format(pulse_length))
#     pulse *= 1000
#     pulse //= pulse_length
#     pwm.set_pwm(channel, 0, pulse)


# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)
# Move servo on channel O between extremes.
logging.info("Start testing servos")
pwm.set_pwm(0, 0, servo_min)
time.sleep(1)
pwm.set_pwm(0, 0, servo_max)
time.sleep(1)
pwm.set_pwm(1, 0, servo_min)
time.sleep(1)
pwm.set_pwm(1, 0, servo_max)
time.sleep(1)
pwm.set_pwm(2, 0, servo_min)
time.sleep(1)
pwm.set_pwm(2, 0, servo_max)


app = Flask(__name__)

# What Raspberry Pi revision are we running?
#  0 = Compute Module, 1 = Rev 1, 2 = Rev 2, 3 = Model B+
GPIO.RPI_REVISION

# What version of RPi.GPIO are we running?
GPIO.VERSION

# GPIO.setmode(GPIO.BCM)

sendQueue = queue.Queue()
#receiveQueue = queue.Queue()

# # Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    27: {'name': 'PLAY ONE', 'state': GPIO.LOW},
    22: {'name': 'PLAY TWO', 'state': GPIO.LOW},
    23: {'name': 'RESET Hand Pay', 'state': GPIO.LOW}  # ,
    #  24 : {'name' : 'YELLOW TURN A', 'state' : GPIO.LOW},
    #   10 : {'name' : 'GREEN TURN A', 'state' : GPIO.LOW},
    #   5 : {'name' : 'RED LIGHT B', 'state' : GPIO.LOW},
    #   6 : {'name' : 'YELLOW LIGHT B', 'state' : GPIO.LOW},
    #   13 : {'name' : 'GREEN LIGHT B', 'state' : GPIO.LOW},
    #   19 : {'name' : 'YELLOW TURN B', 'state' : GPIO.LOW},
    #   26 : {'name' : 'GREEN TURN B', 'state' : GPIO.LOW}
}
# # Create a dictionary called servos to store the servo number, name, and servo state:
servos = {
    0: {'name': 'PLAY ONE', 'state': servo_max},
    1: {'name': 'PLAY TWO', 'state': servo_max},
    2: {'name': 'RESET KEY', 'state': servo_max},
    3: {'name': 'SPARE', 'state': servo_max},

}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# # Set each pin as an output and make it low:
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


@app.route("/")
def processURLRequest():
    logger.info("Process URL Request...")

    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
    print("pins {}", pins)
    logger.info("pins: {} ", pins)
    for servo in servos:
        servos[servo]['state'] = servo_max

    # Along with the pin dictionary, put the modes into the template data dictionary:
    templateData = {
        'pins': pins,
        'servos': servos
    }

    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:

        
@app.route("/<changePin>/<action>")
def action(changePin, action):

    changePin = int(changePin)
    # Get the device name for the pin being changed:
    # Currently unused
    deviceName = pins[changePin]['name']  # DM debugg
    deviceState = pins[changePin]['state']  # DM debugg

    # If the action part of the URL is "on," execute the code indented below:
    print("deviceName: ", deviceName)
    print("deviceState: ", deviceState)
    
    # if changePin == 28:
    #   return render_template('main.html', **templateData )
    global srv
    global cPin # used in thread moveFingers()
    global test
    
    cPin = changePin
    if changePin == 27:
        srv = 0
    if changePin == 23:
        srv = 1
    if changePin == 22:
        srv = 2
    if action == "on":
        global animals
        if test.is_alive() == True:
            animals = 'First stop running'
        else:
            test.start()
        # Set the pin high:
        logger.info("changePin action on:  ", changePin)
        
    if action == "off":
        if test.is_alive() == True:
            logger.info ("stop 1")
            testStopEvent.set()
            test.join() # Wait for the thread to finish
            test = threading.Thread(name ='retest',target=moveFingers, args=((testStopEvent,))) # "re-start" thread
            testStopEvent.clear() # Reset the stop event
            logger.info("stop 2") 
        elif test.is_alive != False:
            logger.info("stop 3")        
        logger.info("changePin action off:",changePin)
        GPIO.output(changePin, GPIO.HIGH)  # LOW
        pwm.set_pwm(srv, 0, servo_max)
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
        
    # Along with the pin dictionary, put the modes into the template data dictionary:
    templateData = {
        'pins': pins 
    }
    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **templateData)

def main():
    # Log some info about the platform
    logger.info("RPi version: {}".format(GPIO.RPI_REVISION))
    logger.info("GPIO version: {}".format(GPIO.VERSION))
    print("Hello world")

    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    time.sleep(1)
    app.run(host='0.0.0.0', port=80, debug=False)

    # I don't think we ever get here but just in case let's terminate the process
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":
    # Setup the logger
    logger = logger.setupLogger("INFO", "INFO", "app")

    # Execute only if run as a script
    main()

# https://prateekvjoshi.com/2016/03/08/how-to-create-a-web-server-in-python-using-flask/
# https://mdbootstrap.com/docs/jquery/components/buttons/
