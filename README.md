This is a software developent project conducted at DHBW Karlsruhe, 01/2020 - 03/2020.
Students: Natalie Keicher - 7577073, Martin Graf - 4294471, David Monninger - 1335605
 
Subject of this project is building a model of an automated high-bay warehouse. 
A gripper driven by 3 NEMA 17 stepper motors can pick up a storage container from a shelf with 16 storage locations. One of these locations
is accessible from the front and can be used as the input/output space for the user.
each storage container has an unique number that can e input using an usb numberpad. The remaining keys of the number pad
are used as control keys ("num lock" --> ESC, "/" --> Input container, "*" --> Output container). A 16x2 lcd is used to return information to the user.

Everything is controlled by a Rasbperry Pi 3 Model B+ in conjunction with 3 A4988 stepper motor drivers.
Managing the current contents of the storage area ist done using an external mySQL database. 