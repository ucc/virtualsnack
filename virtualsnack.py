#!/usr/bin/env python
import npyscreen
from datetime import datetime

# Incorporates code
# from http://www.binarytides.com/python-socket-server-code-example/
# Socket server in python using select function
import socket, select, errno

# for emulator code
import sys
import string

class ContainedMultiSelect(npyscreen.BoxTitle):
    _contained_widget = npyscreen.TitleMultiSelect

class SnackButtonPress(npyscreen.MiniButtonPress):
    def __init__(self, screen, when_pressed_function=None, when_pressed_callback=None, *args, **keywords):
	super(SnackButtonPress, self).__init__(screen, *args, **keywords)
	self.when_pressed_callback = when_pressed_callback

    def whenPressed(self,key=None):
	if self.when_pressed_callback:
		self.when_pressed_callback(widget=self)

class Switches:
    def __init__(self):
        self.misc_input = 0xff
        self.switch_input = 0x3f
    def door_open(self):
        return self.switch_input & 0x20
    def set_door_open(self, open = True):
        if open:
            self.switch_input |= 0x20
        else:
            self.switch_input &= ~0x20


class VirtualSnack(npyscreen.Form):

    def while_waiting(self):
        self.date_widget.value = datetime.now().ctime()
	self.sentfield.value = self.parentApp.sent
	self.receivedfield.value = self.parentApp.received
	self.textdisplay.value = self.parentApp.textdisplay
        self.display()

    def create(self, *args, **keywords):
        super(VirtualSnack, self).create(*args, **keywords)

        self.textdisplay = self.add(npyscreen.FixedText, value=self.parentApp.textdisplay, editable=False, relx=9)
        self.textdisplay.important = True
	
	self.kpbuttons = []
	kpx = 1
	kpy = 1
	for keypad in range(0,10):
		kpx = ((keypad % 4) * 6 ) + 3
		kpy = int(keypad / 4) + 4
		widget = self.add(SnackButtonPress,name="%d"%keypad, relx = kpx, rely = kpy, when_pressed_callback=self.parentApp.when_keypad_pressed)
		self.kpbuttons.append(widget)
		self.add_handlers({"%d"%keypad: widget.whenPressed})
		
	self.reset=self.add(SnackButtonPress,name="RESET",  relx = kpx + 7, rely = kpy, when_pressed_callback=self.parentApp.when_reset_pressed)
	self.add_handlers({"R": self.reset.whenPressed})
	self.add_handlers({"r": self.reset.whenPressed})

	self.door = self.add(npyscreen.MultiSelect, name = "Door", max_width=15, relx = 4, rely = 12, max_height=4, value = [], values = ["DOOR"], scroll_exit=True, value_changed_callback=self.parentApp.when_door_toggled)

	self.dip = self.add(npyscreen.MultiSelect, name = "DIP Switch", max_width=10, rely =3, relx = 35, max_height=10, value = [], values = ["DIP1", "DIP2", "DIP3","DIP4","DIP5","DIP6","DIP7","DIP8"], scroll_exit=True)

	self.nickel=self.add(SnackButtonPress,name="0.05", rely= 3, relx=50)
	self.dime=self.add(SnackButtonPress,name="0.10", relx=50)
	self.quarter=self.add(SnackButtonPress,name="0.25", relx=50)
	self.dollar=self.add(SnackButtonPress,name="1.00", relx=50)

	self.mode=self.add(SnackButtonPress,name="MODE", relx=50)

	
	self.date_widget = self.add(npyscreen.FixedText, value=datetime.now().ctime(), editable=False, rely=18)
        self.date_widget.value = "Hello"
	self.add_handlers({"^Q": self.exit_application})
        
	self.sentfield = self.add(npyscreen.TitleText, name = "Sent:", value="", editable=False, rely=20 )
        self.receivedfield = self.add(npyscreen.TitleText, name = "Received:", value="", editable=False )

    def exit_application(self,name):
        self.parentApp.setNextForm(None)
        self.editing = False


class VirtualSnackApp(npyscreen.NPSAppManaged):
    keypress_timeout_default = 1

    def onStart(self):
	# initialise virtual vending machine
        # vending machine password set here
        self.vendpw = "AAAAAAAAAAAAAAAA"
        self.switches = Switches()
	self.textdisplay = "*5N4CK0RZ*"

	self.F = self.addForm("MAIN", VirtualSnack, name="Virtual Snack")
	
	# socket code
    	self.CONNECTION_LIST = []    # list of socket clients
    	self.RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    	PORT = 5150

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this has no effect, why ?
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", PORT))
        self.server_socket.listen(10)
     
        # Add server socket to the list of readable connections
        self.CONNECTION_LIST.append(self.server_socket)

	self.sent=""
	self.received="Chat server started on port " + str(PORT)

    def while_waiting(self):
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(self.CONNECTION_LIST,[],[],0.01)
 
        for sock in read_sockets:
             
            #New connection
            if sock == self.server_socket:
                # Handle the case in which there is a new connection recieved through self.server_socket
                sockfd, addr = self.server_socket.accept()
                self.CONNECTION_LIST.append(sockfd)
                self.received = "Client (%s, %s) connected" % addr

		self.do_send("000 Virtual Snack is alive \n")
		self.do_prompt()
                 
                #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(self.RECV_BUFFER)
                    # echo back the client message
                    if data:
			self.handle_command(data)
			#response = 'OK ... ' + data
                        #sock.send(response)
			#self.sent = response
			self.received = data
                 
                 
                # client disconnected, so remove from socket list
                except:
                    #print "Client (%s, %s) is offline" % addr
                    sock.close()
                    #self.CONNECTION_LIST.remove(sock)
                    continue
             

    def onCleanExit(self):
        self.server_socket.close()
    
    # Snack Emulator comms below
    
    def do_send(self, data):
        # Get the list sockets which are ready to be written through select
        read_sockets,write_sockets,error_sockets = select.select([],self.CONNECTION_LIST,[],0.01)
 
        for sock in write_sockets:
		try:
			sock.send(data)
		except socket.error, e:
			if isinstance(e.args, tuple):
				self.sent = "errno is %d" % e[0]
				if e[0] == errno.EPIPE:
				# remote peer disconnected
					self.sent = "Detected remote disconnect"
				else:
				# determine and handle different error
					pass
			else:
				self.sent = "socket error ", e
               		self.CONNECTION_LIST.remove(sock)
			sock.close()
			return
		except IOError, e:
			# Hmmm, Can IOError actually be raised by the socket module?
			self.sent = "Got IOError: ", e
			return

	self.sent = data


    # Callbacks
    def when_door_toggled(self, *args, **keywords):
# See 
#  https://code.google.com/p/npyscreen/source/detail?r=9768a97fd80ed1e7b3e670f312564c19b1adfef8#
# for callback info
        if keywords['widget'].get_selected_objects():
            self.do_send('401 door closed\n')
        else:
            self.do_send('400 door open\n')

    def when_reset_pressed(self, *args, **keywords):
        self.do_send('211 keypress\n')
        keywords['widget'].value = False
	self.F.display()

    def when_keypad_pressed(self, *args, **keywords):
	key = '0'+ keywords['widget'].name
        self.do_send('2'+key+' keypress\n')
        keywords['widget'].value = False
	self.F.display()

    # Snack Emulator code below

    def do_prompt(self):
        self.do_send("# ")

    def do_help(self):
        help = """

Valid commands are:
ABOUT         ROM information
B[S][nn]      beep [synchronously] for a duration nn (optional)
C[S][nn]      silence [synchronously] for a duration nn (optional)
Dxxxxxxxxxx   show a message on the display
ECHO {ON|OFF} turn echo on or off
GETROM        download the ROM source code using xmodem
H[...]        this help screen
*JUMPxxxx      jumps to a subroutine at location xxxx
*PEEKxxxx      returns the value of the byte at location xxxx
*POKExxxxyy    sets the value of location xxxx to yy
PING          pongs
S[...]        query all internal switch states
+Vnn           vend an item
+VALL          vend all items
*Wxxxxxxxxxxxx set a new password for authenticated vends. xxx=16 chars
                   password will be converted to uppercase

Very few functions are available when the machine is in standalone
mode (DIP SW 1 is set)
+ denotes that this item requires authentication if DIP SW 2 is set
* denotes that DIP SW 3 must be set to use these
Commands starting with # are ignored (comments)
"""
        self.do_send(help)

    def do_about(self):
        about = """

The Virtual Vending^WSnack Machine Company

Mark Tearle, October 2014
"""
        self.do_send(about)

    def do_vend_all(self):
        for i in range(11,99):
            self.do_send("101 Vending "+str(i)+"\n")
            self.do_send("153 Home sensors failing\n")
        self.do_send("102 Vend all motors complete\n")

    def do_vend(self,command):
        fail = None
        if fail:
            self.do_send("153 Home sensors failing\n")
        else:
	# FIXME
        #     self.insert("Vending "+command)
            self.do_send("100 Vend successful\n")

    def do_display(self,string):
        self.textdisplay = "%-10.10s" % (string)
        self.do_send('300 Written\n')

    def do_beep(self,command):
        sys.stdout.write("\a")
        self.do_send('500 Beeped\n')

    def do_silence(self,command):
        pass

    def do_switches(self):
        self.do_send("600 3F 3F\n")

    def do_pong(self):
        self.do_send("000 PONG!\n")

    def do_echo(self):
        self.do_send("000 Not implemented\n")

    def handle_command(self, command):
        command = string.upper(command)
        if string.find(command, "HELP",0) == 0:
            self.do_help()
        elif string.find(command, "ECHO",0) == 0:
            self.do_echo()
        elif string.find(command, "ABOUT",0) == 0:
            self.do_about()
        elif string.find(command, "PING",0) == 0:
            self.do_pong()
        elif string.find(command, "VALL",0) == 0:
            self.do_vend_all()
        elif string.find(command, "V",0) == 0:
            self.do_vend(command)
        elif string.find(command, "B",0) == 0:
            self.do_beep(command)
        elif string.find(command, "C",0) == 0:
            self.do_silence(command)
        elif string.find(command, "S",0) == 0:
            self.do_switches()
        elif string.find(command, "D",0) == 0:
            self.do_display(command[1:])
        self.do_prompt()

if __name__ == "__main__":
    App = VirtualSnackApp()
    App.run()
