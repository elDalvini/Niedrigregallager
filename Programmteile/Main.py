
import RPi.GPIO as GPIO
import time
import threading
from Stepper import *
import keyboard
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
from KeyboardInput import *
import mysql.connector

#mysql connection:
mydb = mysql.connector.connect(host = "localhost", user = "sManager", passwd = "root", database = "niedrigregallager")
mycursor = mydb.cursor()

#GPIO Pins
XH = 17     #x-axis limit switch
YH = 27     #y-axis limit switch
ZH = 22     #z-axis limit switch
INP = 4     #I/O field sense switch
GRP = 5     #Gripper sense switch

#DIR/STEP pins of all axis
XDIR = 19
XSTEP = 26
YDIR = 6
YSTEP = 13
ZDIR = 10
ZSTEP = 9

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
inpR = false
outR = false
inpD = false
outD = false


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

	    #Start both threads and wait for them to finish
        MovX.start()
        MovY.start()
        MovX.join()
        MovY.join()
    except :
        lcd.clear()
        lcd.display_string('ERROR',1)
        while 1:
            pass


def Pickup():   #Move Z axis forward, raise Y axis, move Z axis back to pick up a box
    try:
        mZ.MoveUntil(10)
        mX.SafeStep(5,1)
        mZ.SafeHome(0)
    except :
        lcd.clear()
        lcd.display_string('ERROR',1)
        while 1:
            pass

def Place():    #Raise Y axis, move Z axis forward, lower Y axis, move Z axis back to put down a box
    try:
        mX.SafeStep(5,1)
        mZ.SafeMove(10)
        mX.Step(5,0)
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
	if key == "w":
		mX.Step(1,1)
	elif key == "s":
		mX.Step(1,0)
	elif key == "a":
		mY.Step(1,1)
	elif key == "d":
		mY.Step(1,0)
	elif key == "r":
		mZ.Step(1,1)
	elif key == "f":
		mZ.Step(1,0)

	#output current position
	print("X: "+str(mX.steps)+"\t Y: "+str(mY.steps)+"\t Z: "+str(mZ.steps))

def hookKeys():
    #attach ManMove to respective keys
    keyboard.on_press_key("w", ManMove)
    keyboard.on_press_key("s", ManMove)
    keyboard.on_press_key("a", ManMove)
    keyboard.on_press_key("d", ManMove)
    keyboard.on_press_key("r", ManMove)
    keyboard.on_press_key("f", ManMove)

    #attach Input/Output functions to respective keys
    keyboard.on_press_key("/", InputR)
    keyboard.on_press_key("*", OutputR)

    #attach HomeAll to q key
    keyboard.on_press_key("q", HomeAll)


#set state variables if an Input/Output is requested:
def InputR(k):            
    inpR = true

def OutputR(k):
    outR = true

def InputD(k):            
    inpD = true

def OutputD(k):
    outD = true



def HomeAll(k=True):
    #Home all axis
    mZ.Home(0)
    mX.Home(0)
    mY.Home(0)


HomeAll()
hookKeys()
MoveXY(800, 800)


while True:
    break
    if inpR:
        keyboard.unhook(Output)
        keyboard.unhook(Input)
        while True:
            if GPIO.input(INP) == 0:
                number = KBinput("Eingabe: ", lcd)
                if number == -1:
                    break
                mycursor.execute('SELECT x,y FROM store WHERE contents = -1')
                coords = mycursor.fetchall()
                mycursor.execute('SELECT  FROM store WHERE contents = %s',str(coords[0][0]))
                x = mycursor.fetchall()[0]
                mycursor.execute('SELECT  FROM store WHERE contents = %s',str(coords[0][1]))
                y = mycursor.fetchall()[0]

                MoveXY(0,0)
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
        inpR = false
        hookKeys()


    if outR:
        keyboard.unhook(Output)
        keyboard.unhook(Input)
        while True:
            if GPIO.input(INP):
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
        outR = false
        hookKeys()



