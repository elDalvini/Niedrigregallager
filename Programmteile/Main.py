
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
mX = Stepper(XSTEP, XDIR, 0.005, XH, GRP)
mY = Stepper(YSTEP, YDIR, 0.005, YH, GRP)
mZ = Stepper(ZSTEP, ZDIR, 0.01, ZH, GRP)



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

def Pickup():
    mZ.Move(10)
    mX.Step(5,1)
    mZ.Home(0)

def Place():
    mX.Step(5,1)
    mZ.Move(10)
    mX.Step(5,0)
    mZ.Home(0)

#Move all axis manually if an arrow key or page up/down is pressed
def ManMove(keypress):
	#print("Manual Mode")
	key = keypress.name
	#print(key)

	if key == "up":
		mX.Step(1,1)
	elif key == "down":
		mX.Step(1,0)
	elif key == "left":
		mY.Step(1,1)
	elif key == "right":
		mY.Step(1,0)
	elif key == "page up":
		mZ.Step(1,1)
	elif key == "page down":
		mZ.Step(1,0)

	#output current position
	print("X: "+str(mX.steps)+"\t Y: "+str(mY.steps)+"\t Z: "+str(mZ.steps))

def hookKeys():
    #attach ManMove to arrow keys
    keyboard.on_press_key("up", ManMove)
    keyboard.on_press_key("down", ManMove)
    keyboard.on_press_key("left", ManMove)
    keyboard.on_press_key("right", ManMove)
    keyboard.on_press_key("page up", ManMove)
    keyboard.on_press_key("page down", ManMove)
    keyboard.on_press_key("÷", Input)
    keyboard.on_press_key("×", Output)
    keyboard.on_press_key("q", HomeAll)

def Input(k):            
    keyboard.unhook_all_hotkeys()
    while True:
        if GPIO.input(INP) == 0:
            number = KBinput("Eingabe: ", lcd)
            if number == -1:
                break
            mycursor.execute('SELECT x,y FROM store WHERE contents = -1')
            coords = mycursor.fetchall()
            MoveXY(0,0)
            Pickup()
            MoveXY(coords[0][0], coords[0][1])
            Place()
            MoveXY(0,0)
        else:
            lcd.clear()
            lcd.display_string("Geben Sie eine Box ein!",1)
            if keyboard.is_pressed("num lock"):
                break
    hookKeys()


def Output():
    keyboard.unhook_all_hotkeys()
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
        else:
            lcd.clear()
            lcd.display_string("Leeren Sie die Ausgabebox!",1)
            if keyboard.is_pressed("num lock"):
                break
    hookKeys()

def HomeAll(k=True):
    #Home all axis
    mX.Home(0)
    mY.Home(0)
    mZ.Home(0)


HomeAll()
hookKeys()
MoveXY(800, 800)


#while True:
#    pass



