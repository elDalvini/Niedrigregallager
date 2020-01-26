
import RPi.GPIO as GPIO
import time
import threading
from Stepper import *
import keyboard
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under
                        #GNU General Public license v2.0 at:
                        #https://github.com/sweetpi/python-i2c-lcd
from KeyboardInput import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#LCD Object definition
lcd = lcddriver.lcd()

#Stepper Object definition
mX = Stepper(19, 26, 0.005, 14)
mY = Stepper(6, 13, 0.005, 15)
mZ = Stepper(16, 20, 0.01, 18)

#Home all axis
#mX.Home(0)
#mY.Home(0)
#mZ.Home(0)

def MoveXY(x,y):	#Moves the carrier to a specific point
	if x == 0:	#whether to use Home() or Move()
	    MovX = threading.Thread(target = mX.Home, args = (0,))
	else:
		MovX = threading.Thread(target = mX.Move, args = (x,))

	if y == 0:	#whether to use Home() or Move()
	    MovY = threading.Thread(target = mY.Home, args = (0,))
	else:
		MovY = threading.Thread(target = mY.Move, args = (y,))

	#Start both threads and wait for them to finish
	MovX.start()
	MovY.start()
	MovX.join()
	MovY.join()

def Pickup():
	pass

def ManMove(keypress):
	#print("Manual Mode")
	key = keypress.name
	#print(key)

	if key == "up":
		mX.Step(1,1)
	elif key == "down":
		mX.Step(1,0)
	elif key == "left":
		mY.Step(1,1)
	elif key == "right":
		mY.Step(1,0)
	elif key == "x":
		return()


keyboard.on_press_key("up", ManMove)
keyboard.on_press_key("down", ManMove)
keyboard.on_press_key("left", ManMove)
keyboard.on_press_key("right", ManMove)


MoveXY(200,200)
MoveXY(1,1)

while True:
    pass
	


