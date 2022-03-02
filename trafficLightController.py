#!/usr/bin/python3
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#    trafficLightController.py
#    copyright 2019 Aptiv
#
#    A very basic traffic light controller used for
#    controlling a 3-section or 5-section Traffic light for
#    the Aptiv Las Vegas Test Track.
#
#    Controls
#    RED LIGHT
#    YELLOW LIGHT
#    GREEN LIGHT
#    YELLOW TURN
#    GREEN TURN
#
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#    3/9/2019 Don Bush - created file
#------------------------------------------------------------------------------------------------------------------------------------------------------------

import os
import queue as queue
import logger
import threading
import random
import time
from datetime import datetime
import RPi.GPIO as GPIO

# All values are in seconds
# Cycle time phase 1 cycleTime = G1 + Y1 + R1 (Clearence times))
# CYCLE_LENGTH = GREEN_CLEARANCE + YELLOW_CLEARANCE + RED_CLEARANCE 
# Average cycle time is 120 seconds                     
CYCLE_LENGTH = 120
# Average clearance time is 60 seconds                     
RED_CLEARANCE = 58
# Average clearance time is 3 to 6 seconds                     
YELLOW_CLEARANCE = 4
YELLOW_LEFT_CLEARANCE = 4
# Average clearance time is 60 seconds                     
GREEN_CLEARANCE = 58
GREEN_LEFT_CLEARANCE = 20
GREEN_TURN_START = 15
GREEN_TURN_CLEARANCE = 15

CAUTION_FLASH_CYCLE = 1
EMERGENCY_FLASH_CYCLE = 1
HEARTBEAT_FLASH_CYCLE = 1
HEARTBEAT_PIN = 25

exit_event = threading.Event()
receiveQueue = queue.Queue()

class TrafficLightController():    
    def __init__(self, name, pins, inQueue, outQueue):
        self.name = name
        self.pins = pins
        self.inQueue = inQueue
        self.outQueue = outQueue

        self.currentState = 'stateInitialize'        

        self.currentPhase = 'phaseInit'        
        self.currentTrafficLightState = 'stateGreenLight'        

        self.heartbeatPin = HEARTBEAT_PIN
        GPIO.setup(self.heartbeatPin, GPIO.OUT)

        self.cautionFlashRate = CAUTION_FLASH_CYCLE/2
        self.emergencyFlashRate = EMERGENCY_FLASH_CYCLE/2

        self.toggleCycle = 0
        self.toggleHeartbeat = 0
        
        self.idleHeartbeatCycleRate = HEARTBEAT_FLASH_CYCLE/2
        self.hbStartTime =  time.time()                     
        self.hbEndTime =  0                     
        
        self.runningHeartbeatCycleRate = HEARTBEAT_FLASH_CYCLE/5

        self.startCycleTime = 0
        self.endCycleTime = 0
        
        self.startTime = 0
        self.endTime = 0

        self.greenLeftTurnCleared = False
        self.yellowLeftTurnCleared = True
 
        # Setup the logger
        self.logger = logger.setupLogger("INFO","INFO",self.name)

        self.thread = threading.Thread(target=self.run, name=self.name + "Thread")
        self.thread.start()
    
    def __str__(self):
        return "{name:s}".format(name=self.name)

    def getPinNumber(self, name):
        for pin in self.pins:
            if(self.pins[pin]['name'] == name):
                return pin
        return 0

    def run(self):
      self.logger.info("TrafficLightController started...")

      while not exit_event.isSet():
           # Non-Blocking queue
           try:
               data = self.inQueue.get(False)
           except queue.Empty:
               data = None                

           if self.currentState == 'stateInitialize':
               if data == 'StartTrafficLightController':
                  self.currentState = 'stateReset'
                   
           elif self.currentState == 'stateReset':
               # Turn off all lights
               for pin in self.pins:
                   GPIO.output(pin, GPIO.LOW)
               
               self.currentTrafficLightState = 'stateRedLight'        

               self.currentState = 'stateIdle'

           elif self.currentState == 'stateIdle':
               # Heart is beating slowly...      	  
               self.controllerHeartbeat(self.idleHeartbeatCycleRate)

           	   # We're normally in idle just waiting for a command
               if data == '2-Way Stop Mode':
                   self.startTime = time.time()
                   self.currentState = 'state2WayStopMode'
                   self.currentPhase = 'phaseInit'        
                   self.currentTrafficLightState = 'stateGreenLight'        
               elif data == '4-Way Stop Mode':
                   self.startTime = time.time()
                   self.currentState = 'state4WayStopMode'
                   self.currentPhase = 'phaseInit'
                   self.currentTrafficLightState = 'stateGreenLight'        
               elif data == '3-Section Light Mode':
                   self.startTime = time.time()
                   self.currentState = 'state3SectionLightMode'
                   self.currentPhase = 'phaseInit'        
                   self.currentTrafficLightState = 'stateGreenLight'        
               elif data == '5-Section Light Mode':
                   self.startTime = time.time()
                   self.currentState = 'state5SectionLightMode'
                   self.currentPhase = 'phaseInit'        
                   self.currentTrafficLightState = 'stateGreenLight'        
               elif data == 'Caution Mode':
                   self.toggleCycle = 0
                   self.startTime = time.time()
                   self.currentState = 'stateCaution'
               elif data == 'Emergency Mode':
                   self.logger.info(self.name + "Starting Emergency Mode...")
                   self.toggleCycle = 0
                   self.startTime = time.time()
                   self.currentState = 'stateEmergency'
               elif data == 'StopTrafficLightController':
                   # Exit the thread
                   self.outQueue.put("TrafficLightControllerStopped")
                   exit_event.set()

           elif self.currentState == 'stateCaution':
              if data == 'StopAllModes':
                  self.currentState = 'stateReset'
              else:
                  pins = {self.getPinNumber('YELLOW LIGHT A'), self.getPinNumber('YELLOW LIGHT B')}
                  self.flashTrafficLights(pins, self.cautionFlashRate)
                  # Heart is beating faster...      	  
                  self.controllerHeartbeat(self.runningHeartbeatCycleRate)

           elif self.currentState == 'stateEmergency':
              if data == 'StopAllModes':
                  self.currentState = 'stateReset'
              else:
                  pins = {self.getPinNumber('RED LIGHT A'), self.getPinNumber('RED LIGHT B')}
                  self.flashTrafficLights(pins, self.emergencyFlashRate)
                  # Heart is beating faster...      	  
                  self.controllerHeartbeat(self.runningHeartbeatCycleRate)

           elif self.currentState == 'state4WayStopMode':
              if data == 'StopAllModes':
                  self.currentState = 'stateReset'
              #else:
                  #self.sequenceTrafficLight('4WayMode')
                  # Heart is beating faster...      	  
                  #self.controllerHeartbeat(self.runningHeartbeatCycleRate)

           elif self.currentState == 'state2WayStopMode':
              if data == 'StopAllModes':
                  self.currentState = 'stateReset'
              #else:
                  #self.sequenceTrafficLight('2WayMode')
                  # Heart is beating faster...      	  
                  #self.controllerHeartbeat(self.runningHeartbeatCycleRate)
            	
           elif self.currentState == 'state3SectionLightMode':
              if data == 'StopAllModes':
                  self.currentState = 'stateReset'
              else:
                  self.sequenceTrafficLight('3SectionLightMode')
                  # Heart is beating faster...      	  
                  self.controllerHeartbeat(self.runningHeartbeatCycleRate)

           elif self.currentState == 'state5SectionLightMode':
              if data == 'StopAllModes':
                  self.currentState = 'stateReset'
              else:
                  self.sequenceTrafficLight('5SectionLightMode')
                  # Heart is beating faster...      	  
                  self.controllerHeartbeat(self.runningHeartbeatCycleRate)

      self.logger.info("TrafficLightController stopped!")

    def controllerHeartbeat(self, cycleRate):
        # Get the current end time
        self.hbEndTime = time.time()
        if (self.hbEndTime - self.hbStartTime >= cycleRate):
            if (self.toggleHeartbeat == 0):
                GPIO.output(self.heartbeatPin, GPIO.HIGH)
            else:
                GPIO.output(self.heartbeatPin, GPIO.LOW)
            # Toggle the flag            
            self.toggleHeartbeat ^= 1                  
            # Reset the start time            
            self.hbStartTime =  time.time()                     

    def flashTrafficLights(self,pins,cycleTime):
        # Get the current end time
        self.endTime = time.time()
        # Flash the lights                  
        if (self.endTime - self.startTime >= cycleTime):
            if (self.toggleCycle == 0):
                for pin in pins:
                    GPIO.output(pin, GPIO.HIGH)
            else:
                for pin in pins:
                    GPIO.output(pin, GPIO.LOW)
            # Toggle the flag            
            self.toggleCycle ^= 1                  
            # Reset the start time            
            self.startTime =  time.time()                     

    def sequenceTrafficLight(self, mode):
        mode = mode
        if mode == '3SectionLightMode':
	        # Get the current end time
	        self.endTime = time.time()
	        if self.currentPhase == 'phaseInit':
	            # Turn on the green light to start
	            GPIO.output(self.getPinNumber('GREEN LIGHT A'), GPIO.HIGH)
	            self.currentPhase = 'phaseOne'
	            
	        if self.currentPhase == 'phaseOne':
	            if self.currentTrafficLightState == 'stateGreenLight':
	                # Green light clearance time                     
	                if (self.endTime - self.startTime >= GREEN_CLEARANCE):
	                    # Turn off the green light
	                    GPIO.output(self.getPinNumber('GREEN LIGHT A'), GPIO.LOW)
	                    # Turn on the yellow light
	                    GPIO.output(self.getPinNumber('YELLOW LIGHT A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateYellowLight'
	
	            elif self.currentTrafficLightState == 'stateYellowLight':
	                # Yellow light clearance time
	                if (self.endTime - self.startTime >= YELLOW_CLEARANCE):
	                    # Turn off the yellow light A
	                    GPIO.output(self.getPinNumber('YELLOW LIGHT A'), GPIO.LOW)
	                    # Turn on the red light
	                    GPIO.output(self.getPinNumber('RED LIGHT A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateRedLight'
	
	            elif self.currentTrafficLightState == 'stateRedLight':
	                # Red light clearance time                     
	                if (self.endTime - self.startTime >= RED_CLEARANCE):
	                    # Turn off the red light
	                    GPIO.output(self.getPinNumber('RED LIGHT A'), GPIO.LOW)
	                    # Turn on the green light
	                    GPIO.output(self.getPinNumber('GREEN LIGHT A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateGreenLight'
	                    
        elif mode == '5SectionLightMode':
	        # Get the current end time
	        self.endTime = time.time()
	        if self.currentPhase == 'phaseInit':
	            # Turn on the green light to start
	            GPIO.output(self.getPinNumber('GREEN LIGHT A'), GPIO.HIGH)
	            self.currentPhase = 'phaseOne'
	            
	        if self.currentPhase == 'phaseOne':
	            if self.currentTrafficLightState == 'stateGreenLight':
	                # Green light clearance time                     
	                if (self.endTime - self.startTime >= GREEN_CLEARANCE):
	                    # Turn off the green light
	                    GPIO.output(self.getPinNumber('GREEN LIGHT A'), GPIO.LOW)
	                    # Turn on the yellow light
	                    GPIO.output(self.getPinNumber('YELLOW LIGHT A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateYellowLight'
	
	            elif self.currentTrafficLightState == 'stateYellowLight':
	                # Yellow light clearance time
	                if (self.endTime - self.startTime >= YELLOW_CLEARANCE):
	                    # Turn off the yellow light A
	                    GPIO.output(self.getPinNumber('YELLOW LIGHT A'), GPIO.LOW)
	                    # Turn on the red light
	                    GPIO.output(self.getPinNumber('RED LIGHT A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateRedLight'
	
	            elif self.currentTrafficLightState == 'stateRedLight':
	                # Green turn start time                     
	                if (self.endTime - self.startTime >= GREEN_TURN_START):
	                    # Turn on the green turn light
	                    GPIO.output(self.getPinNumber('GREEN TURN A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateRedGreenTurnLight'

	            elif self.currentTrafficLightState == 'stateRedGreenTurnLight':
	                # Green turn clearance time                     
	                if (self.endTime - self.startTime >= GREEN_TURN_CLEARANCE):
	                    # Turn off the red light
	                    GPIO.output(self.getPinNumber('GREEN TURN A'), GPIO.LOW)
	                    # Turn on the green light
	                    GPIO.output(self.getPinNumber('YELLOW TURN A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateRedYellowTurnLight'

	            elif self.currentTrafficLightState == 'stateRedYellowTurnLight':
	                # Red light clearance time                     
	                if (self.endTime - self.startTime >= YELLOW_CLEARANCE):
	                    # Turn off the red light
	                    GPIO.output(self.getPinNumber('YELLOW TURN A'), GPIO.LOW)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateRedLightEnd'
            
	            elif self.currentTrafficLightState == 'stateRedLightEnd':
	                # Red light clearance time                     
	                if (self.endTime - self.startTime >= RED_CLEARANCE/2):
	                    # Turn off the red light
	                    GPIO.output(self.getPinNumber('RED LIGHT A'), GPIO.LOW)
	                    # Turn off the red light
	                    GPIO.output(self.getPinNumber('GREEN LIGHT A'), GPIO.HIGH)
	                    # Reset the timer 
	                    self.startTime =  time.time()
	                    self.currentTrafficLightState = 'stateGreenLight'

