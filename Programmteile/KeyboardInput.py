import keyboard
import RPi.GPIO as GPIO
import time
import lcddriver

#from RpiMotorLib import RpiMotorlib

lcd = lcddriver.lcd()


GPIO.setmode(GPIO.BCM)
GPIO.setup(14,GPIO.OUT)

def input(title):
    lcd.display_string(title,1)
    x = ""
    ltime = 0
    prevKey = ""
    while 1:
        key = keyboard.read_key()
        
        if (key == prevKey and time.time_ns() - ltime >  250000000) or key != prevKey:
            ltime = time.time_ns()
            if key in ["1","2","3","4","5","6","7","8","9","0"]:
                    x += key
            elif key == "enter":
                lcd.clear()
                if x != "":
                    return(x)
                else:
                    lcd.display_string("Bitte gueltige",1)
                    lcd.display_string("Zahl eingeben!",2)
                    time.sleep(0.75)
            elif key == "+":
                    x = x[:-1]
            lcd.clear()
            lcd.display_string(title,1)
            lcd.display_string(x,2)
            prevKey = key

print(input("Eingabe:"))