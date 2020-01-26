def input(title, lcd):   #gets a number by keyboard input, live input and title are displayed on the LCD.
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

            elif key == "enter":    #breaks loop, returns result
                lcd.clear()
                if x != "":
                    return(x)
                else:               #display error if the result is empty
                    lcd.display_string("Bitte gueltige",1)
                    lcd.display_string("Zahl eingeben!",2)
                    time.sleep(0.75)

            elif key == "+":        #the '+'-Key is used as backspace --> remove last character from result
                    x = x[:-1]

            #Update LCD
            lcd.clear()
            lcd.display_string(title,1)
            lcd.display_string(x,2)
            prevKey = key
