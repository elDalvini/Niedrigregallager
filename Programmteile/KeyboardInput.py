
import keyboard
import RPi.GPIO as GPIO
import time
import lcddriver

#from RpiMotorLib import RpiMotorlib

lcd = lcddriver.lcd()

GPIO.setmode(GPIO.BCM)
GPIO.setup(14,GPIO.OUT)

x = ""
prevKey = ""

while 1:
        key = keyboard.read_key()
        if key != prevKey:
                time.sleep(0.01)
                if key in ["1","2","3","4","5","6","7","8","9","0"]:
                        x += key
                elif key == "enter":
                        print(x)
                        x = ""
                elif key == "+":
                        x = x[:-1]
                lcd.clear()
                lcd.display_string(x,0)
                prevKey = key
