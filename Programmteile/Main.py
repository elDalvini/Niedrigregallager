#! /usr/bin/python3
#########################################################################################################################
# This is a software developent project conducted at DHBW Karlsruhe, 01/2020 - 03/2020.
# Students: Natalie Keicher - 7577073, Martin Graf - 4294471, David Monninger - 1335605
# 
# Subject of this project is building a model of an automated high-bay warehouse. 
# A gripper driven by 3 NEMA 17 stepper motors can pick up a storage container from a shelf with 16 storage locations. One of these locations
# is accessible from the front and can be used as the input/output space for the user.
# each storage container has an unique number that can e input using an usb numberpad. The remaining keys of the number pad
# are used as control keys ("num lock" --> ESC, "/" --> Input container, "*" --> Output container). A 16x2 lcd is used to return information to the user.
# 
# Everything is controlled by a Rasbperry Pi 3 Model B+ in conjunction with 3 A4988 stepper motor drivers.
# Managing the current contents of the storage area ist done using an external mySQL database. 
#########################################################################################################################


####################################setup, variable definitions etc.######################################################

#library imports
import RPi.GPIO as GPIO     #Raspberry Pi GPIO library
import time                 #time library for various delays in the program
import threading            #threading library to perform multiple task (i.e. drive multiple motors) at once
import lcddriver            #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
import mysql.connector      #mySQL connector library for reading/changing the current contents of the strage locations
import subprocess           #subprocess library to test availability of the mySQL server
import keyboard             #keyboard library for numberpad input

from KeyboardInput_i2 import *  #custom library to get a number from user input at the numberpad while displaying typed numbers at the LCD
from Stepper import *           #custom library to drive the stepper motors

#LCD Object definition
lcd = lcddriver.lcd()
lcd.display_string('Start...', 1)   #display first sign of life

#wait for the mySQL service to become avaliable
while subprocess.Popen('service mysqld status', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').find('Active: active') == -1:
    time.sleep(1)

#setup mysql connection
mydb = mysql.connector.connect(host = "localhost", user = "sManager", passwd = "root", database = "niedrigregallager")
mycursor = mydb.cursor()

#define GPIO Pins
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
mX = Stepper(XSTEP, XDIR, 0.005, XH, GRP)   #x-axis (left-right)
mY = Stepper(YSTEP, YDIR, 0.01, YH, GRP)    #y-axis (up-down)
mZ = Stepper(ZSTEP, ZDIR, 0.005, ZH, GRP)   #z-axis (gripper front-back)

#Status Variables:
inpR = False    #requested input by container number
outR = False    #requested output by container number

#Coordinates:
IOX = 1529      #x-coordinate of input/output location
IOY = 50        #y-coordinate of input/output location
ZP = 638        #amount the gripper travels forward to pick up a container
IOHop = 150     #amount the gripper travels up to pick up a container


#######################################Function definitions#######################################################

def MoveXY(x,y):	#Moves the carrier to a specific point
    #creation of threads for Movement of both axis
    #(threads are used so that both axis can move at the same time)
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

def SafeMoveXY(x,y):	#Moves the carrier to a specific point, gives an error if the container ist lost along the way
    try:    #try/catch is used to react to losing a container

        #creation of threads for Movement of both axis
        #(threads are used so that both axis can move at the same time)
        if x == 0:	#whether to use SafeHome() or SafeMove()
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

    except :    #container lost
        #display error message
        lcd.clear()
        lcd.display_string('ERROR',1)

        #after 3 seconds, return all axis to their resting place to enable a safe shutdown
        time.sleep(3)
        HomeAll()
        #do nothing until the next reboot
        while 1:
            pass


def Pickup():   #Move Z axis forward, raise Y axis, move Z axis back to pick up a box
    try:
        mZ.Move(ZP)
        mY.Step(IOHop,1)
        mZ.SafeHome(0)
    except :    #error handling the same way as in the SafeMoveXY function
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
    except :    #error handling the same way as in the SafeMoveXY function
        lcd.clear()
        lcd.display_string('ERROR',1)
        time.sleep(3)
        HomeAll()
        while 1:
            pass

#Move all axis manually if arrow keys or page up/down are pressed
#This function is not supposed to be used other than for debugging. 
#It can only be used by connecting a full size keyboard instead or alongside the numberpad
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

	#output current position to Terminal
	print("X: "+str(mX.steps)+"\t Y: "+str(mY.steps)+"\t Z: "+str(mZ.steps))

def hookKeys():     #function to attach functions to pressed keys
    #attach ManMove to respective keys (only for debugging)
    keyboard.on_press_key("up", ManMove)
    keyboard.on_press_key("down", ManMove)
    keyboard.on_press_key("left", ManMove)
    keyboard.on_press_key("right", ManMove)
    keyboard.on_press_key("page up", ManMove)
    keyboard.on_press_key("page down", ManMove)

    #attach Input/Output functions to their respective keys
    keyboard.on_press_key("÷", InputR)
    keyboard.on_press_key("×", OutputR)

    #attach HomeAll to q key (only for debugging)
    keyboard.on_press_key("q", HomeAll)


#set state variables if an Input/Output is requested:
def InputR(k):            
    global inpR
    inpR = True

def OutputR(k):
    global outR
    outR = True

#function to home all axis
def HomeAll(k=True):
    #Home all axis
    mZ.Home(0)
    mX.Home(0)
    mY.Home(0)

############################################Start actually doing something#########################################


HomeAll()   #home all axis after startup
hookKeys()  #attach hotkeys to their respective functions

lcd.clear() #clear lcd to indicate successful startup

while True: #main loop
    
    #Input a container by container number if status variable is set
    if inpR:
        keyboard.unhook_all()   #ignore all unwanted keypresses during input

        while True:

            #check whether the I/O-location is occupied
            if GPIO.input(INP) == True: 

                number = KBinput("Eingabe: ", lcd)  #get number of new container vie KeyboardInput library
                if number == '-1':  #"num lock" --> ESC key was pressed during number input -> cancel execution, break loop
                    break

                lcd.display_string('In Arbeit...',1)    

                mycursor.execute('SELECT x,y FROM store WHERE contents ='+str(number))  #check if the input number ist already in the database
                if len(mycursor.fetchall()) != 0:   #if it is, display error and cancel execution
                    lcd.display_string("Nummer schon",1)
                    lcd.display_string("vorhanden!",2)
                    time.sleep(1.5)
                    lcd.clear()
                    break

                #get next free location (by column and row) from the database, store result
                mycursor.execute('SELECT x,y FROM store WHERE contents = -1')
                coords = mycursor.fetchall()

                if len(coords) == 0:    #if there is no free space avaliable, display error and cancel execution
                    lcd.display_string('Lager voll!',1)
                    time.sleep(1.5)
                    lcd.clear()
                    break

                #get coordinates of the storage space from two more database tables (the coordinates are stored this way to make fine tuning easier)
                mycursor.execute('SELECT coords FROM row WHERE number = '+str(coords[0][0]))
                y = mycursor.fetchall()[0][0]
                mycursor.execute('SELECT coords FROM columns WHERE number = '+str(coords[0][1]))
                x = mycursor.fetchall()[0][0]

                MoveXY(IOX,IOY) #move the gripper to the I/O location
                Pickup()        #Pick up new container
                SafeMoveXY(x, y)    #move to the next free sorage space
                Place()         #Place the container there

                #update database with the new container number
                mycursor.execute('UPDATE store SET contents = ' + str(number) + ' WHERE x = ' + str(coords[0][0]) + ' AND y = ' + str(coords[0][1]))
                mydb.commit()   #commit changes to the database

                MoveXY(0,0)     #move the gripper to its resting place
                lcd.clear()     #clear display to indicate end of current action
                break   #break loop

            else:   #no container is detected in the I/O location
                #display error until a container is placed there
                lcd.clear()
                lcd.display_string("Geben Sie eine", 1)
                lcd.display_string("Box ein!", 2)
                time.sleep(0.2)

                #clear display, cancel execution and break loop if "num lock" --> ESC is pressed
                if keyboard.is_pressed("num lock"):
                    lcd.clear()
                    break

        inpR = False    #reset status variable
        hookKeys()      #start again listening to keypresses 

    #Output a container by container number if status variable is set
    if outR:
        keyboard.unhook_all()   #ignore all unwanted keypresses during output

        while True:

            #check whether the I/O-location is occupied
            if not GPIO.input(INP):

                number = KBinput("Ausgabe: ", lcd)  #get number of requested container vie KeyboardInput library
                if number == '-1':  #"num lock" --> ESC key was pressed during number input -> cancel execution, break loop
                    break

                lcd.display_string('In Arbeit...',1)

                #get location of the requested container (by column and row) from the database, store result
                mycursor.execute('SELECT x,y FROM store WHERE contents ='+str(number))
                coords = mycursor.fetchall()

                if len(coords) == 0:    #if the requested container is not found, display error and cancel execution
                    lcd.display_string('Nicht gefunden!',1)
                    time.sleep(1.5)
                    lcd.clear()
                    break

                #get coordinates of the storage space from two more database tables (the coordinates are stored this way to make fine tuning easier)
                mycursor.execute('SELECT coords FROM row WHERE number = '+str(coords[0][0]))
                y = mycursor.fetchall()[0][0]
                mycursor.execute('SELECT coords FROM columns WHERE number = '+str(coords[0][1]))
                x = mycursor.fetchall()[0][0]

                MoveXY(x, y)    #move the gripper to he location of the requested container
                Pickup()        #pick up this container
                SafeMoveXY(IOX,IOY) #move the gripper to the I/O location
                Place()         #Place the container there

                #update database, set previous location of the output container to empty
                mycursor.execute('UPDATE store SET contents = -1 WHERE x = ' + str(coords[0][0]) + ' AND y = ' + str(coords[0][1]))
                mydb.commit()   #commit changes to the database

                MoveXY(0,0)     #move the gripper to its resting place
                lcd.clear()     #clear display to indicate end of current action
                break   #break loop

            else:   #a container is detected in the I/O location
                #display error until the container is removed
                lcd.clear()
                lcd.display_string("Leeren Sie die",1)
                lcd.display_string("Ausgabebox!",2)
                time.sleep(0.2)

                #clear display, cancel execution and break loop if "num lock" --> ESC is pressed
                if keyboard.is_pressed("num lock"):
                    lcd.clear()
                    break
        outR = False    #reset status variable
        hookKeys()      #start again listening to keypresses 



