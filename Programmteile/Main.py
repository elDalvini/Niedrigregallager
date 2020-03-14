
import RPi.GPIO as GPIO
import time
import threading
from Stepper import *
import keyboard
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
from KeyboardInput_i2 import *
import mysql.connector

#mysql connection:
mydb = mysql.connector.connect(host = "localhost", user = "sManager", passwd = "root", database = "niedrigregallager")
mycursor = mydb.cursor()

#GPIO Pins
XH = 21     #x-axis limit switch
YH = 20     #y-axis limit switch
ZH = 16     #z-axis limit switch
INP = 8     #I/O field sense switch
GRP = 7     #Gripper sense switch

#DIR/STEP pins of all axis
XDIR = 19
XSTEP = 26
YDIR = 6
YSTEP = 13
ZDIR = 11
ZSTEP = 5

#GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(INP, GPIO.IN)
GPIO.setup(GRP, GPIO.IN)

#LCD Object definition
lcd = lcddriver.lcd()

#Stepper Object definition
mX = Stepper(XSTEP, XDIR, 0.01, XH, GRP)
mY = Stepper(YSTEP, YDIR, 0.01, YH, GRP)
mZ = Stepper(ZSTEP, ZDIR, 0.01, ZH, GRP)

#Status Variables:
inpR = False
outR = False
inpD = False
outD = False

#Coordinates:
IOX = 1510
IOY = 87
ZP = 638
IOHop = 77


def MoveXY(x,y):	#Moves the carrier to a specific point
	if x == 0:	#whether to use Home() or Move()
	    MovX = threading.Thread(target = mX.Home, args = (0,))
	else:
		MovX = threading.Thread(target = mX.Move, args = (x,))

	if y == 0:	#whether to use Home() or Move()
	    MovY = threading.Thread(target = mY.Home, args = (0,))
	else:
		MovY = threading.Thread(target = mY.Move, args = (y,))

	#Start both threads and wait for them to finish
	MovX.start()
	MovY.start()
	MovX.join()
	MovY.join()

def SafeMoveXY(x,y):	#Moves the carrier to a specific point
    try:
        if x == 0:	#whether to use Home() or Move()
            MovX = threading.Thread(target = mX.SafeHome, args = (0,))
        else:
            MovX = threading.Thread(target = mX.SafeMove, args = (x,))

        if y == 0:	#whether to use Home() or Move()
            MovY = threading.Thread(target = mY.SafeHome, args = (0,))
        else:
            MovY = threading.Thread(target = mY.SafeMove, args = (y,))

	    #Start both threads and wait for them to finish (using threads so both axis can move at the same time)
        MovX.start()
        MovY.start()
        MovX.join()
        MovY.join()
    except :
        lcd.clear()
        lcd.display_string('ERROR',1)
        while 1:
            pass


def Pickup():   #Move Z axis forward until sense switch is pressed, raise Y axis, move Z axis back to pick up a box
    try:
        mZ.MoveUntil(ZP)
        mY.SafeStep(IOHop,1)
        mZ.SafeHome(0)
    except :
        lcd.clear()
        lcd.display_string('ERROR',1)
        while 1:
            pass

def Place():    #Raise Y axis, move Z axis forward, lower Y axis, move Z axis back to put down a box
    try:
        mY.SafeStep(IOHop,1)
        mZ.SafeMove(ZP-30)
        mY.Step(IOHop,0)
        mZ.Home(0)
    except :
        lcd.clear()
        lcd.display_string('ERROR',1)
        while 1:
            pass

#Move all axis manually if w/a/s/d/r/f is pressed
def ManMove(keypress):
	key = keypress.name #get pressed key

    #step respective axis by one step up or down
	if key == "up":
		mY.Step(1,1)
	elif key == "down":
		mY.Step(1,0)
	elif key == "left":
		mX.Step(1,1)
	elif key == "right":
		mX.Step(1,0)
	elif key == "page up":
		mZ.Step(1,1)
	elif key == "page down":
		mZ.Step(1,0)

	#output current position
	print("X: "+str(mX.steps)+"\t Y: "+str(mY.steps)+"\t Z: "+str(mZ.steps))

def hookKeys():
    #attach ManMove to respective keys
    keyboard.on_press_key("up", ManMove)
    keyboard.on_press_key("down", ManMove)
    keyboard.on_press_key("left", ManMove)
    keyboard.on_press_key("right", ManMove)
    keyboard.on_press_key("page up", ManMove)
    keyboard.on_press_key("page down", ManMove)

    #attach Input/Output functions to respective keys
    keyboard.on_press_key("÷", InputR)
    keyboard.on_press_key("×", OutputR)

    #attach HomeAll to q key
    keyboard.on_press_key("q", HomeAll)


#set state variables if an Input/Output is requested:
def InputR(k):            
    global inpR
    inpR = True

def OutputR(k):
    global outR
    outR = True

def InputD(k): 
    global inpD
    inpD = True

def OutputD(k):
    global outD
    outD = True



def HomeAll(k=True):
    #Home all axis
    mZ.Home(0)
    mX.Home(0)
    mY.Home(0)


HomeAll()
hookKeys()
#MoveXY(800, 800)


while True:
    #break
    if inpR:
        keyboard.unhook_all()
        keyboard.unhook_all()
        while True:
            if GPIO.input(INP) == True:
                number = KBinput("Eingabe: ", lcd)
                if number == -1:
                    break
                mycursor.execute('SELECT x,y FROM store WHERE contents = -1')
                coords = mycursor.fetchall()
                mycursor.execute('SELECT coords FROM row WHERE number = '+str(coords[0][0]))
                y = mycursor.fetchall()[0][0]
                mycursor.execute('SELECT coords FROM columns WHERE number = '+str(coords[0][1]))
                x = mycursor.fetchall()[0][0]

                MoveXY(IOX,IOY)
                Pickup()
                MoveXY(x, y)
                Place()
                MoveXY(0,0)
                break
            else:
                lcd.clear()
                lcd.display_string("Geben Sie eine Box ein!",1)
                if keyboard.is_pressed("num lock"):
                    break
        inpR = False
        hookKeys()


    if outR:
        keyboard.unhook_all()
        keyboard.unhook_all()
        while True:
            if not GPIO.input(INP):
                number = KBinput("Ausgabe: ", lcd)
                if number == -1:
                    break
                mycursor.execute('SELECT x,y FROM store WHERE contents ='+str(number))
                coords = mycursor.fetchall()
                MoveXY(coords[0][0], coords[0][1])
                Pickup()
                MoveXY(0,0)
                Place()
                break
            else:
                lcd.clear()
                lcd.display_string("Leeren Sie die Ausgabebox!",1)
                if keyboard.is_pressed("num lock"):
                    break
        outR = False
        hookKeys()



