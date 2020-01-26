
import RPi.GPIO as GPIO
import time
import threading
from Stepper import *
import keyboard
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
from KeyboardInput import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#LCD Object definition 
lcd = lcddriver.lcd()

#Stepper Object definition
mX = Stepper(19, 26, 0.005, 14)
mY = Stepper(6, 13, 0.005, 15)
mZ = Stepper(16, 20, 0.01, 18)

#mX.Home(0)
#mY.Home(0)
#mZ.Home(0)


def MoveXY(x,y):
	if x == 0:
	    MovX = threading.Thread(target = mX.Home, args = (0))
	else:
		MovX = threading.Thread(target = mX.Move, args = (x))

	if y == 0:
	    MovY = threading.Thread(target = mY.Home, args = (0))
	else:
		MovY = threading.Thread(target = mY.Move, args = (y))
	MovX.start()
	MovY.start()
	MovX.join()
	MovY.join()


MoveXY(200,200)
	


