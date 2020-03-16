#! /usr/bin/python3
#########################################################################################################################
# This is a software developent project conducted at DHBW Karlsruhe, 01/2020 - 03/2020.
# Students: Natalie Keicher -7577073, Martin Graf - 4294471, David Monninger - 1335605
# 
# Subject of this project is building a model of an automated high-bay warehouse. 
# A gripper driven by 3 stepper motors can pick up a storage container from a shelf with 16 storage locations. One of these locations
# is accessible from the front and can be used as the input/output space for the user. 

import RPi.GPIO as GPIO
import time
import threading
from Stepper import *
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
import mysql.connector
import subprocess

#LCD Object definition
lcd = lcddriver.lcd()
lcd.display_string('Start...', 1)

while subprocess.Popen('service mysqld status', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').find('Active: active') == -1:
    time.sleep(1)

import keyboard
from KeyboardInput_i2 import *

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

#Stepper Object definition
mX = Stepper(XSTEP, XDIR, 0.005, XH, GRP)
mY = Stepper(YSTEP, YDIR, 0.01, YH, GRP)
mZ = Stepper(ZSTEP, ZDIR, 0.005, ZH, GRP)

#Status Variables:
inpR = False
outR = False
inpD = False
outD = False

#Coordinates:
IOX = 1529
IOY = 87
ZP = 638
IOHop = 150


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
        time.sleep(3)
        HomeAll()
        while 1:
            pass


def Pickup():   #Move Z axis forward until sense switch is pressed, raise Y axis, move Z axis back to pick up a box
    try:
        mZ.Move(ZP)
        mY.Step(IOHop,1)
        mZ.SafeHome(0)
    except :
        lcd.clear()
        lcd.display_string('ERROR',1)
        time.sleep(3)
        HomeAll()
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
        time.sleep(3)
        HomeAll()
        while 1:
            pass

#Move all axis manually if arrow keys or page up/down are pressed
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

lcd.clear()
#MoveXY(800, 800)


while True:
    #break
    if inpR:
        keyboard.unhook_all()
        keyboard.unhook_all()
        while True:
            if GPIO.input(INP) == True:
                number = KBinput("Eingabe: ", lcd)
                if number == '-1':
                    break
                lcd.display_string('In Arbeit...',1)
                mycursor.execute('SELECT x,y FROM store WHERE contents ='+str(number))
                if len(mycursor.fetchall()) != 0:
                    lcd.display_string("Nummer schon",1)
                    lcd.display_string("vorhanden!",2)
                    time.sleep(1.5)
                    lcd.clear()
                    break
                mycursor.execute('SELECT x,y FROM store WHERE contents = -1')
                coords = mycursor.fetchall()
                if len(coords) == 0:
                    lcd.display_string('Lager voll!',1)
                    time.sleep(1.5)
                    lcd.clear()
                    break
                mycursor.execute('SELECT coords FROM row WHERE number = '+str(coords[0][0]))
                y = mycursor.fetchall()[0][0]
                mycursor.execute('SELECT coords FROM columns WHERE number = '+str(coords[0][1]))
                x = mycursor.fetchall()[0][0]

                MoveXY(IOX,IOY)
                Pickup()
                MoveXY(x, y)
                Place()
                mycursor.execute('UPDATE store SET contents = ' + str(number) + ' WHERE x = ' + str(coords[0][0]) + ' AND y = ' + str(coords[0][1]))
                mydb.commit()
                MoveXY(0,0)
                lcd.clear()
                break
            else:
                lcd.clear()
                lcd.display_string("Geben Sie eine", 1)
                lcd.display_string("Box ein!", 2)
                time.sleep(0.2)
                if keyboard.is_pressed("num lock"):
                    lcd.clear()
                    break
        inpR = False
        hookKeys()


    if outR:
        keyboard.unhook_all()
        keyboard.unhook_all()
        while True:
            if not GPIO.input(INP):
                number = KBinput("Ausgabe: ", lcd)
                if number == '-1':
                    break
                lcd.display_string('In Arbeit...',1)
                mycursor.execute('SELECT x,y FROM store WHERE contents ='+str(number))
                coords = mycursor.fetchall()
                if len(coords) == 0:
                    lcd.display_string('Nicht gefunden!',1)
                    time.sleep(1.5)
                    lcd.clear()
                    break
                mycursor.execute('SELECT coords FROM row WHERE number = '+str(coords[0][0]))
                y = mycursor.fetchall()[0][0]
                mycursor.execute('SELECT coords FROM columns WHERE number = '+str(coords[0][1]))
                x = mycursor.fetchall()[0][0]


                MoveXY(x, y)
                Pickup()
                MoveXY(IOX,IOY)
                Place()
                mycursor.execute('UPDATE store SET contents = -1 WHERE x = ' + str(coords[0][0]) + ' AND y = ' + str(coords[0][1]))
                mydb.commit()
                MoveXY(0,0)
                lcd.clear()
                break
            else:
                lcd.clear()
                lcd.display_string("Leeren Sie die",1)
                lcd.display_string("Ausgabebox!",2)
                time.sleep(0.2)
                if keyboard.is_pressed("num lock"):
                    lcd.clear()
                    break
        outR = False
        hookKeys()



