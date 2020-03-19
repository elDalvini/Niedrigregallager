#########################################################################################################################
# This is a software developent project conducted at DHBW Karlsruhe, 01/2020 - 03/2020.
# Students: Natalie Keicher -7577073, Martin Graf - 4294471, David Monninger - 1335605
# 
# This library handles user input of a number via the number pad, typed numbers are displayed at an LCD. 
# For further details about the project see Main.py
#########################################################################################################################

####################################setup, variable definitions etc.######################################################

#library imports
import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
import time             #time library for various delays in the program
import keyboard         #keyboard library for numberpad input

#Input variable definition
InputString = ""    #typed numbers are stores in this string
available = False   #state variable to indicate end of input

def KBinput(title, lcd):   #gets a number by keyboard input, live input and title are displayed on the LCD.

    #use global variables:
    global InputString
    global available

    lcd.display_string(title,1) #write title to first line of LCD
    
    keyboard.unhook_all_hotkeys()   #stop listening to any previous hotkeys

    #attach InputNumber function to all number keys
    keyboard.on_press_key("0", InputNumber)
    keyboard.on_press_key("1", InputNumber)
    keyboard.on_press_key("2", InputNumber)
    keyboard.on_press_key("3", InputNumber)
    keyboard.on_press_key("4", InputNumber)
    keyboard.on_press_key("5", InputNumber)
    keyboard.on_press_key("6", InputNumber)
    keyboard.on_press_key("7", InputNumber)
    keyboard.on_press_key("8", InputNumber)
    keyboard.on_press_key("9", InputNumber)
    keyboard.on_press_key("num lock", InputNumber)
    keyboard.on_press_key("enter", InputNumber)
    keyboard.on_press_key("backspace", InputNumber)

    while 1:    #wait for end of input

        if available:
            if InputString != "":   #a number has been typed

                lcd.clear()
                keyboard.unhook_all()   #stop listening to number keys
                out = InputString       #store input string
                InputString = ""        #reset InputString variable for next input
                available = False       #reset state variable

                return(out) #return result, end function

            else:   #no number has been typed
                #display error message, reset state variable, then continue as before
                lcd.display_string("Bitte gueltige",1)
                lcd.display_string("Zahl eingeben!",2)
                time.sleep(0.75)
                available = False

        #update LCD with currently typed numbers and title of Input
        lcd.clear()
        if InputString != -1:
            lcd.display_string(title,1)
            lcd.display_string(InputString,2)
            time.sleep(0.2)


def InputNumber(keypress):  #function to change InputString if a number key ist pressed

    #use global variables
    global InputString
    global available

    key = keypress.name #get pressed keys
    
    #append number keys to result 
    if key in ["1","2","3","4","5","6","7","8","9","0"]: 
        InputString += key

    #enter breaks loop, returns result (by setting state variable)
    elif key == "enter":    
        available = True

    #backspace removes last character from result
    elif key == "backspace":        
        InputString = InputString[:-1]

    #num lock --> ESC sets result to -1, returns it
    elif key == "num lock":
        InputString = '-1'
        available = True