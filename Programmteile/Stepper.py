import RPi.GPIO as GPIO
import time
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class Stepper:
    steps = 0       #current Position
    StepPin = 0     #GPIO connected to 'STEP' Pin of A4988 driver
    DirPin = 0      #GPIO connected to 'DIR' Pin of A4988 driver
    EndPin = -1     #GPIO connected to optional end switch (normally closed), -1 if none connected  
    Delay = 0       #Delay between steps (in seconds)

    #Initialisation:
    def __init__(self, Step, Dir, StepDelay, End = -1):
        #store set Values of the Motor:
        self.steps = 0
        self.StepPin = Step
        self.DirPin = Dir
        self.Delay = StepDelay
        self.EndPin = End

        #Setup GPIOs
        GPIO.setup(self.StepPin, GPIO.OUT)
        GPIO.setup(self.DirPin, GPIO.OUT)
        if self.EndPin != -1:   #only setup GPIO or Endswitch if one is connected
            GPIO.setup(self.EndPin, GPIO.IN)

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

        
#Stepper Object definition
mX = Stepper(19, 26, 0.005, 5)
mY = Stepper(6, 13, 0.005)

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


