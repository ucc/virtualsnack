virtualsnack
============

Curses based emulator of the UCC Snack Machine ROM

Usage
-----

virtualsnack.py

Via the network:
	Connect to port 5150 to issue commands as per Snack ROM interface.

Via the console:
	Keypad numbers (0-9) emit via the network connection valid response
	Reset is mapped to R
	Door acts as a toggle


Requirements
-------------

* npyscreen 4.6.1 or later

Known Issues
-------------

1. DIP Switches are not currently working
2. MODE and Money buttons are not implemented (nor are they in the Snack ROM)
