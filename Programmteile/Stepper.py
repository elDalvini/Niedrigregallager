
#from RpiMotorLib import RpiMotorLib

#motor = RpiMotorLib.BYJMotor("a","nema")

#motor.motor_run([19,21,26,13],0.001, 5000,0,0,"full",0)     #([pins], delay, steps, ccwise, verbose, "stepType", initDelay)

import RPi.GPIO as GPIO
import time
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class Stepper:
    steps = 0
    StepPin = 0
    DirPin = 0
    EndPin = 0
    Delay = 0


    def __init__(self, Step, Dir, StepDelay, End = -1):
        self.steps = 0
        self.StepPin = Step
        self.DirPin = Dir
        self.Delay = StepDelay
        self.EndPin = End
        GPIO.setup(self.StepPin, GPIO.OUT)
        GPIO.setup(self.DirPin, GPIO.OUT)
        if self.EndPin != -1:
            GPIO.setup(self.EndPin, GPIO.IN)

    def Step(self, steps, dir):
        GPIO.output(self.DirPin, dir)
        for i in range(steps):
            GPIO.output(self.StepPin,1)
            time.sleep(self.Delay/2)
            GPIO.output(self.StepPin,0)
            time.sleep(self.Delay/2)

            self.steps += (dir*2-1)

    def Move(self, pos):
        if pos != self.steps:
            dir = not (pos < self.steps)
            self.Step(abs(self.steps - pos), dir)

    def Home(self,dir):
        if self.EndPin != -1:
            while GPIO.input(self.EndPin):
                self.Step(1,dir)

        

mX = Stepper(19, 26, 0.005, 5)
mY = Stepper(6, 13, 0.005)

mX.Step(150,1)
time.sleep(0.25)
mX.Move(75)
time.sleep(0.5)
mX.Home(0)

#MovX = threading.Thread(target = mX.Step , args=(500,1))
#MovY = threading.Thread(target = mY.Step, args = (100,0))
#MovX.start()
#time.sleep(1)
#MovY.start()
#MovY.join()
#print("Y done")
#MovX.join()
#print("X done")


#mX.Step(50,1)
#print(str(mX.steps))
#time.sleep(0.25)
#mY.Step(50,1)
#print(str(mX.steps))
#time.sleep(0.25)
#mX.Step(25,0)
#print(str(mX.steps))


