
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

    def __init__(Step, Dir):
        steps = 0
        StepPin = Step
        DirPin = Dir
        GPIO.setup(StepPin, GPIO.OUT)
        GPIO.setup(DirPin, GPIO.OUT)

    def Step(steps, dir, ):
        GPIO.output(DirPin, )

