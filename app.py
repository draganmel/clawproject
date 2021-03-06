#!/usr/bin/python3
'''
Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson
Modified by Rui Santos
Complete project details: http://randomnerdtutorials.com
'''
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#    app.py
#    copyright 2019 Aptiv
#
#    App controlling Traffic lights and other Traffic
#    signals at the Aptiv Las Vegas Test Track.
#
#    Controls
#    Traffic Light Controller 2-Way and 4-Way
#
#    To run automatically at boot.
#    sudo nano /etc/rc.local
#    sudo python3 /home/pi/Documents/web-server/app.py &
#
#    5 section right turn
#    https://www.youtube.com/watch?v=hmtWjQx2J6E
#    green yellow red red-greenright red-yellowright red --> green
#
#    5 section left turn
#    https://www.youtube.com/watch?v=MdrPzCq8QbU
#    green yellow red red-greenleft green-greenleft green-yellowleft --> green
#
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#    3/1/2019 Matthew Brown - created file
#    3/9/2019 Don Bush - added trafficLightController
#    11/2/2022 Don and Dragan start modification for Claw Project
#------------------------------------------------------------------------------------------------------------------------------------------------------------

import os
import time
import logger
import signal
#import threading
import queue as queue
import trafficLightController
import RPi.GPIO as GPIO

from flask import Flask, render_template, request
#from __future__ import division


# Import the PCA9685 module.
import Adafruit_PCA9685
# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()
# Configure min and max servo pulse lengths
servo_min = 250  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)
# Move servo on channel O between extremes.
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

#GPIO.setmode(GPIO.BCM)

#exit_event = threading.Event()
 
#sendQueue = queue.Queue()
#receiveQueue = queue.Queue()
 
# # Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   27 : {'name' : 'PLAY ONE', 'state' : GPIO.LOW},
   22 : {'name' : 'PLAY TWO', 'state' : GPIO.LOW},
   23 : {'name' : 'RESET HP', 'state' : GPIO.LOW}#,
   #24 : {'name' : 'YELLOW TURN A', 'state' : GPIO.LOW},
#   10 : {'name' : 'GREEN TURN A', 'state' : GPIO.LOW},
#   5 : {'name' : 'RED LIGHT B', 'state' : GPIO.LOW},
#   6 : {'name' : 'YELLOW LIGHT B', 'state' : GPIO.LOW},
#   13 : {'name' : 'GREEN LIGHT B', 'state' : GPIO.LOW},
#   19 : {'name' : 'YELLOW TURN B', 'state' : GPIO.LOW},
#   26 : {'name' : 'GREEN TURN B', 'state' : GPIO.LOW}
   }
# # Create a dictionary called servos to store the servo number, name, and servo state:
servos = {
   0 : {'name' : 'PLAY ONE', 'state' : servo_max},
   1 : {'name' : 'PLAY TWO', 'state' : servo_max},
   2 : {'name' : 'RESET KEY	', 'state' : servo_max},
   3 : {'name' : 'SPARE', 'state' : servo_max},

   }
# # Create a dictionary called modes to store the mode name, and mode state:
modes = {
   '2-Way Stop Mode' : {'state' : 'off'},
   '4-Way Stop Mode' : {'state' : 'off'},
   '3-Section Light Mode' : {'state' : 'off'},
   '5-Section Light Mode' : {'state' : 'off'},
   'Caution Mode' : {'state' : 'off'},
   'Emergency Mode' : {'state' : 'off'}
   }
   
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# # Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

@app.route("/")
def processURLRequest():
   logger.info("Process URL Request")

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
      
   for servo in servos:
   	servos[servo]['state'] = servo_max
   	
   # Along with the pin dictionary, put the modes into the template data dictionary:
   templateData = {
      'pins' : pins,
      'servos':servos,
      'modes': modes
      }

   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   # Currently unused 
   deviceName = pins[changePin]['name']

 



   #deviceName = servos[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   #print(deviceName)
   srv = int(0) 
   if changePin == 27:
      srv=0
   if changePin == 23:
      srv=1
   if changePin == 22:
      srv=2   
   if action == "on":
      # Set the pin high:
      print(changePin)
      GPIO.output(changePin, GPIO.HIGH)
      pwm.set_pwm(srv, 0, servo_min)
      # Save the status message to be passed into the template:
      # Currently unused 
      #message = "Turned " + deviceName + " on."
   if action == "off":
      print(changePin)
      GPIO.output(changePin, GPIO.LOW)
      pwm.set_pwm(srv, 0, servo_max)
      # Save the status message to be passed into the template:
      # Currently unused 
      #message = "Turned " + deviceName + " off."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the modes into the template data dictionary:
   templateData = {
      'pins' : pins,
      'modes' : modes
   }

   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData )

# @app.route("/mode/<mode>/<state>/")
# def mode(mode,state):
#   # Get the newMode
#   newMode = mode

#   # Get the newState
#   newState = state

#   # Turn off all lights
#   for pin in pins:
#      GPIO.output(pin, GPIO.LOW)

#   # There can be only one state at a time
#   #for mode in modes:
# #      modes[mode]['state']  = 'off'

#   # Save the new state for the new mode
#   #modes[newMode]['state']  = newState

#   sendQueue.put('StopAlltemplateDataModes')
#   # Start or stop the new mode   	
#   #if (newState == 'on'):
# #      sendQueue.put(newMode)

#   # Along with the pin dictionary, put the message into the template data dictionary:
#   #templateData = {
# #      'pins' : pins,
# #      'modes' : modes
# #   }

  # Pass the template data into the template main.html and return it to the user
#  return render_template('main.html', **templateData)
       
def endProcess(signum = None, frame = None):
   #  # Stop the Traffic Light Controller
   #  sendQueue.put('StopTrafficLightController')
 
   #  # Blocking queue
   #  try:
   #      data = receiveQueue.get()
   #  except queue.Empty:
   #      data = None

   # # Waiting for message from traffic light controller to continue
   #  if data == 'TrafficLightControllerStopped':    	
   #     logger.info("Traffic Light Controller Stopped... Continuing to shut down...")

   # # Called on process termination.
   #  if signum is not None:
   #      SIGNAL_NAMES_DICT = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n )
   #      logger.info("signal {} received by process with PID {}".format(SIGNAL_NAMES_DICT[signum], os.getpid()))

   #    #if data == 'TrafficLightControllerStopped':    	  logger.info("Terminating program...")
    
    logger.info("Cleaning up GPIO...")

    GPIO.cleanup()
    
    pwm.set_pwm(0, 0, servo_max)
    pwm.set_pwm(1, 0, servo_max)
    pwm.set_pwm(2, 0, servo_max)
   
    # Give the GPIO plenty of time to settle down
    time.sleep(1)

    # All done, ready to exit    
    logger.info("Done!")
            
    exit(0)
    
def main():
   # Log some info about the platform   
   logger.info("RPi version: {}".format(GPIO.RPI_REVISION))
   logger.info("GPIO version: {}".format(GPIO.VERSION))
   print("Hello world")

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
      
      
   # Assign handler for process exit
   signal.signal(signal.SIGTERM, endProcess)
   signal.signal(signal.SIGINT, endProcess)
   signal.signal(signal.SIGHUP, endProcess)
   signal.signal(signal.SIGQUIT, endProcess)

   # Create Traffic Light Controller
   #trafficLightController.TrafficLightController('TrafficLightController', pins, sendQueue, receiveQueue)
   # Start Traffic Light Controller
  # time.sleep(1)
   #sendQueue.put('StartTrafficLightController')
   # Automatically start in 5-Section Light Mode?   
  # time.sleep(1)
  # sendQueue.put('5-Section Light Mode')
   # Run the server   
   time.sleep(1)
   app.run(host='0.0.0.0', port=80, debug=False)

   # I don't think we ever get here but just in case let's terminate the process   
   os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":
    # Setup the logger
    logger = logger.setupLogger("INFO","INFO","app")

    # Execute only if run as a script
    main()
    
# https://prateekvjoshi.com/2016/03/08/how-to-create-a-web-server-in-python-using-flask/
# https://mdbootstrap.com/docs/jquery/components/buttons/
    
