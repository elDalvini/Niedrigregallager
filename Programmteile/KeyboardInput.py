import lcddriver        #LCD driver library courtesy of Github user sweetpi, published under GNU General Public license v2.0 at: https://github.com/sweetpi/python-i2c-lcd
import time
import keyboard


def KBinput(title, lcd):   #gets a number by keyboard input, live input and title are displayed on the LCD.
    lcd.display_string(title,1) #write title to first line of LCD

    #Variable definition
    x = ""
    ltime = 0
    prevKey = ""

    while 1:
        key = keyboard.read_key()   #read currently pressed key
        
        if (key == prevKey and time.time_ns() - ltime >  250000000) or key != prevKey:  #add delay if the same key is pressed twice in a row --> preventing double presses
            ltime = time.time_ns()

            if key in ["1","2","3","4","5","6","7","8","9","0"]: #append number keys to result 
                    x += key

            elif key == "home":
                x += '7'
            elif key == "up":
                x += '8'
            elif key == "page up":
                x += '9'
            elif key == "left":
                x += '4'
            elif key == "clear":
                x += '5'
            elif key == "right":
                x += '6'
            elif key == "end":
                x += '1'
            elif key == 'down':
                x += '2'
            elif key == 'page down':
                x += '3'
            elif key == 'insert':
                x += '0'

            elif key == "enter":    #breaks loop, returns result
                lcd.clear()
                if x != "":
                    return(x)
                else:               #display error if the result is empty
                    lcd.display_string("Bitte gueltige",1)
                    lcd.display_string("Zahl eingeben!",2)
                    time.sleep(0.75)

            elif key == "backspace":        #remove last character from result
                x = x[:-1]

            elif key == "num lock":
                return(-1)
            #Update LCD
            lcd.clear()
            lcd.display_string(title,1)
            lcd.display_string(x,2)
            prevKey = key
