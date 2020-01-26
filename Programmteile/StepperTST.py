import RPi.GPIO as GPIO
import time
import threading
from Stepper import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

        
#Stepper Object definition
mX = Stepper(19, 26, 0.005, 14)
mY = Stepper(6, 13, 0.005, 15)
mZ = Stepper(16, 20, 0.01, 18)

###########Move and Home example#####

mX.Step(150,1)
time.sleep(0.25)
mX.Move(75)
time.sleep(0.5)
mX.Home(0)


############Threading example########
#
#MovX = threading.Thread(target = mX.Step , args=(500,1))
#MovY = threading.Thread(target = mY.Step, args = (100,0))
#MovX.start()
#time.sleep(1)
#MovY.start()
#MovY.join()
#print("Y done")
#MovX.join()
#print("X done")


##########Step example###############
#
#mX.Step(50,1)
#print(str(mX.steps))
#time.sleep(0.25)
#mY.Step(50,1)
#print(str(mX.steps))
#time.sleep(0.25)
#mX.Step(25,0)
#print(str(mX.steps))


