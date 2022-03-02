# # Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   27 : {'name' : 'RED LIGHT IS ', 'state' : GPIO.LOW},
   22 : {'name' : 'YELLOW LIGHT A', 'state' : GPIO.LOW},
   23 : {'name' : 'GREEN LIGHT A', 'state' : GPIO.LOW}#,
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
   2 : {'name' : 'RESET KEY   ', 'state' : servo_max},
   3 : {'name' : 'YELLOW TURN A', 'state' : servo_max},
   4 : {'name' : 'GREEN TURN A', 'state' : servo_max},
   5 : {'name' : 'RED LIGHT B', 'state' : servo_max},
   6 : {'name' : 'YELLOW LIGHT B', 'state' : servo_max},
   7 : {'name' : 'GREEN LIGHT B', 'state' : servo_max},
   8 : {'name' : 'YELLOW TURN B', 'state' : servo_max},
   9 : {'name' : 'YELLOW TURN B', 'state' : servo_max},
   10 : {'name' : 'YELLOW TURN B', 'state' : servo_max},
   11: {'name' : 'YELLOW TURN B', 'state' : servo_max},
   12: {'name' : 'YELLOW TURN B', 'state' : servo_max},
   13: {'name' : 'YELLOW TURN B', 'state' : servo_max},
   14: {'name' : 'YELLOW TURN B', 'state' : servo_max},
   15: {'name' : 'GREEN TURN B', 'state' : servo_max}
   }
   # The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   # Currently unused 
   deviceName = pins[changePin]['name']
   deviceName = servos[]
   # If the action part of the URL is "on," execute the code indented below:
   print(deviceName)
   if action == "on":
      # Set the pin high:
      print(changePin)
      GPIO.output(changePin, GPIO.HIGH)
      pwm.set_pwm(0, 0, servo_min)
      # Save the status message to be passed into the template:
      # Currently unused 
      #message = "Turned " + deviceName + " on."
   if action == "off":
      print(changePin)
      GPIO.output(changePin, GPIO.LOW)
      pwm.set_pwm(0, 0, servo_max)
      # Save the status message to be passed into the template:
      # Currently unused 
      #message = "Turned " + deviceName + " off."