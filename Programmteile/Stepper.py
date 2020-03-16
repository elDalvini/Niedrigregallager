#########################################################################################################################
# This is a software developent project conducted at DHBW Karlsruhe, 01/2020 - 03/2020.
# Students: Natalie Keicher -7577073, Martin Graf - 4294471, David Monninger - 1335605
# 
# This library handles driving the stepper motors via A4988 driver boards. For further details see Main.py

#library imports
import RPi.GPIO as GPIO     #Raspberry Pi GPIO library
import time                 #time library for timing the steps sent to the stepper motor driver

#definition of stepper class
class Stepper:
    steps = 0       #current Position
    StepPin = 0     #GPIO connected to 'STEP' Pin of A4988 driver
    DirPin = 0      #GPIO connected to 'DIR' Pin of A4988 driver
    EndPin = -1     #GPIO connected to optional end switch (normally closed), -1 if none connected
    GrpPin = -1     #GPIO connected to gripper sense switch 
    Delay = 0       #Delay between steps (in seconds)

    lostSteps = 0   #number of censecutive steps with no container at the gripper, only used by the SafeStep/Move/Home methods (see below)

    #Initialisation:
    def __init__(self, Step, Dir, StepDelay, End = -1, GRP = -1):
        #store set Values of the Motor:
        self.steps = 0
        self.StepPin = Step
        self.DirPin = Dir
        self.Delay = StepDelay
        self.EndPin = End
        self.GrpPin = GRP
        self.lostSteps = 0

        #Setup GPIOs
        GPIO.setup(self.StepPin, GPIO.OUT)
        GPIO.setup(self.DirPin, GPIO.OUT)
        if self.EndPin != -1:   #only setup GPIO for Endswitch if one is connected
            GPIO.setup(self.EndPin, GPIO.IN)        
        
        if self.GrpPin != -1:   #only setup GPIO for Gripper switch if one is connected
            GPIO.setup(self.GrpPin, GPIO.IN)

    #Move a defined number of steps
    def Step(self, steps, dir):
        GPIO.output(self.DirPin, dir)       #set direction

        #pulse STEP output for each step
        for i in range(steps):
            GPIO.output(self.StepPin,1)
            time.sleep(self.Delay/2)
            GPIO.output(self.StepPin,0)
            time.sleep(self.Delay/2)

            self.steps += (dir*2-1)         #increment (or decrement) current position

    #Move to a defined Position
    def Move(self, pos):
        if pos != self.steps:       #do nothing if the motor is already at the defined position 
            dir = not (pos < self.steps)            #set direction
            self.Step(abs(self.steps - pos), dir)   #move the difference between current and determined position

    #Move in the given direction until the end switch is pressed
    def Home(self,dir):
        if self.EndPin != -1:   #do nothing if no end switch is connected
            #move one step at a time until the end switch is pressed
            while not GPIO.input(self.EndPin):
                self.Step(1,dir)

            self.steps = 0  #set current position to zero





#################################### Transport functions (stop moving if the box is lost) ################################################
    #Move a defined number of steps
    def SafeStep(self, steps, dir):
        GPIO.output(self.DirPin, dir)       #set direction

        for i in range(steps):
            #increase lostSteps counter if no container is detected, reset it if there is one detected
            if GPIO.input(self.GrpPin) == True:
                self.lostSteps += 1
            else:
                self.lostSteps = 0

            #raise error if the lostSteps counter ecceds 100
            if self.lostSteps > 100:
                raise RuntimeError

        #pulse STEP output for each step
            GPIO.output(self.StepPin,1)
            time.sleep(self.Delay/2)
            GPIO.output(self.StepPin,0)
            time.sleep(self.Delay/2)

            self.steps += (dir*2-1)         #increment (or decrement) current position    

############### all of the methods below are identical to above methods, they just use the SafeStep() method instead of the Step() method #########
    #Move to a defined Position
    def SafeMove(self, pos):
        if pos != self.steps:       #do nothing if the motor is already at the defined position 
            dir = not (pos < self.steps)            #set direction
            self.SafeStep(abs(self.steps - pos), dir)   #move the difference between current and determined position    
    
    #Move to a defined Position
    def MoveUntil(self, pos):
        if pos != self.steps:       #do nothing if the motor is already at the defined position 
            dir = not (pos < self.steps)            #set direction
            self.StepUntil(abs(self.steps - pos), dir)   #move the difference between current and determined position

    #Move in the given direction until the end switch is pressed
    def SafeHome(self,dir):
        if self.EndPin != -1:   #do nothing if no end switch is connected
            #move one step at a time until the end switch is pressed
            while not GPIO.input(self.EndPin):
                self.SafeStep(1,dir)

            self.steps = 0  #set current position to zero