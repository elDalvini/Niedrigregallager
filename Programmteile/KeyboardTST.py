import keyboard
import RPi.GPIO as GPIO
import time
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
from KeyboardLib import *

lcd = lcddriver.lcd()


GPIO.setmode(GPIO.BCM)
GPIO.setup(14,GPIO.OUT)



print(KBinput("Eingabe:", lcd))