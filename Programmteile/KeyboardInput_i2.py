import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
import time
import keyboard

#Input variable definition
InputString = ""
avaliable = False

def KBinput(title, lcd):   #gets a number by keyboard input, live input and title are displayed on the LCD.
    global InputString

    lcd.display_string(title,1) #write title to first line of LCD
    
    keyboard.unhook_all_hotkeys()
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
    #keyboard.on_press_key("home", InputNumber)
    #keyboard.on_press_key("up", InputNumber)
    #keyboard.on_press_key("page up", InputNumber)
    #keyboard.on_press_key("left", InputNumber)
    #keyboard.on_press_key("clear", InputNumber)
    #keyboard.on_press_key("right", InputNumber)
    #keyboard.on_press_key("end", InputNumber)
    #keyboard.on_press_key("down", InputNumber)
    #keyboard.on_press_key("page down", InputNumber)
    #keyboard.on_press_key("insert", InputNumber)
    keyboard.on_press_key("num lock", InputNumber)
    keyboard.on_press_key("enter", InputNumber)
    keyboard.on_press_key("backspace", InputNumber)

    while 1:
        if avaliable:
            if InputString != "":
                lcd.clear()
                keyboard.unhook_all_hotkeys()
                hookKeys()
                out = InputString
                InputString = ""
                return(out)
            else:
                lcd.display_string("Bitte gueltige",1)
                lcd.display_string("Zahl eingeben!",2)
                time.sleep(0.75)

        lcd.clear()
        lcd.display_string(title,1)
        lcd.display_string(InputString,2)


def InputNumber(keypress):
    global InputString
    key = keypress.name
    if key in ["1","2","3","4","5","6","7","8","9","0"]: #append number keys to result 
        InputString += key

    elif key == "enter":    #breaks loop, returns result
        avaliable = True


    elif key == "backspace":        #remove last character from result
        InputString = InputString[:-1]

    elif key == "num lock":
        InputString = -1
        avaliable = True