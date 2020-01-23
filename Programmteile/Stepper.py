
#from RpiMotorLib import RpiMotorLib

#motor = RpiMotorLib.BYJMotor("a","nema")

#motor.motor_run([19,21,26,13],0.001, 5000,0,0,"full",0)     #([pins], delay, steps, ccwise, verbose, "stepType", initDelay)

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


class Stepper:
    steps = 0
    StepPin = 0
    DirPin = 0
    Delay = 0

    def __init__(self, Step, Dir, StepDelay):
        steps = 0
        StepPin = Step
        DirPin = Dir
        Delay = StepDelay
        GPIO.setup(StepPin, GPIO.OUT)
        GPIO.setup(DirPin, GPIO.OUT)

    def Step(self, steps, dir):
        GPIO.output(DirPin, 1)
        for i in range(steps):
            GPIO.output(StepPin,1)
            time.sleep(Delay/2)
            GPIO.output(StepPin,0)
            time.sleep(Delay/2)

mX = Stepper(19, 26, 0.005)

mX.Step(50,1)


