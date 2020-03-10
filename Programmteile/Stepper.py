
import RPi.GPIO as GPIO
import time

class Stepper:
    steps = 0       #current Position
    StepPin = 0     #GPIO connected to 'STEP' Pin of A4988 driver
    DirPin = 0      #GPIO connected to 'DIR' Pin of A4988 driver
    EndPin = -1     #GPIO connected to optional end switch (normally closed), -1 if none connected
    GrpPin = -1     #GPIO connected to gripper sense switch 
    Delay = 0       #Delay between steps (in seconds)

    #Initialisation:
    def __init__(self, Step, Dir, StepDelay, End = -1, GRP = -1):
        #store set Values of the Motor:
        self.steps = 0
        self.StepPin = Step
        self.DirPin = Dir
        self.Delay = StepDelay
        self.EndPin = End
        self.GrpPin = GRP

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
            while GPIO.input(self.EndPin):
                self.Step(1,dir)

            self.steps = 0  #set current position to zero





#################################### Transport functions (stop moving if the box is lost) ################################################
    #Move a defined number of steps
    def SafeStep(self, steps, dir):
        GPIO.output(self.DirPin, dir)       #set direction

        #pulse STEP output for each step
        for i in range(steps):
            if GPIO.input(self.GrpPin) == True:
                raise RuntimeError
            GPIO.output(self.StepPin,1)
            time.sleep(self.Delay/2)
            GPIO.output(self.StepPin,0)
            time.sleep(self.Delay/2)

            self.steps += (dir*2-1)         #increment (or decrement) current position    

    def StepUntil(self, steps, dir):
        GPIO.output(self.DirPin, dir)       #set direction

        #pulse STEP output for each step
        for i in range(steps):
            if GPIO.input(self.GrpPin) == False:
                break
            GPIO.output(self.StepPin,1)
            time.sleep(self.Delay/2)
            GPIO.output(self.StepPin,0)
            time.sleep(self.Delay/2)

            self.steps += (dir*2-1)         #increment (or decrement) current position

    #Move to a defined Position
    def SafeMove(self, pos):
        if pos != self.steps:       #do nothing if the motor is already at the defined position 
            dir = not (pos < self.steps)            #set direction
            self.SafeStep(abs(self.steps - pos), dir)   #move the difference between current and determined position    
    
    #Move to a defined Position
    def MoveUntil(self, pos):
        if pos != self.steps:       #do nothing if the motor is already at the defined position 
            dir = not (pos < self.steps)            #set direction
            self.SafeStep(abs(self.steps - pos), dir)   #move the difference between current and determined position

    #Move in the given direction until the end switch is pressed
    def SafeHome(self,dir):
        if self.EndPin != -1:   #do nothing if no end switch is connected
            #move one step at a time until the end switch is pressed
            while GPIO.input(self.EndPin):
                self.SafeStep(1,dir)

            self.steps = 0  #set current position to zero