#!/usr/bin/env python
import npyscreen
from datetime import datetime

# Incorporates code
# from http://www.binarytides.com/python-socket-server-code-example/
# Socket server in python using select function
import socket, select

class ContainedMultiSelect(npyscreen.BoxTitle):
    _contained_widget = npyscreen.TitleMultiSelect

class VirtualSnack(npyscreen.Form):

    def while_waiting(self):
        self.date_widget.value = datetime.now().ctime()
	self.sentfield.value = self.parentApp.sent
	self.receivedfield.value = self.parentApp.received
        self.display()


    def create(self, *args, **keywords):
        super(VirtualSnack, self).create(*args, **keywords)


        self.textdisplay = self.add(npyscreen.FixedText, value="*5N4CK0RZ*", editable=False, relx=9)
        self.textdisplay.important = True
	
	self.kpbuttons = []
	kpx = 1
	kpy = 1
	for keypad in range(0,10):
		kpx = ((keypad % 4) * 6 ) + 3
		kpy = int(keypad / 4) + 4
		self.kpbuttons.append(self.add(npyscreen.MiniButton,name="%d"%keypad, relx = kpx, rely = kpy))
		
	self.reset= self.add(npyscreen.MiniButton,name="RESET",  relx = kpx + 7, rely = kpy)

	self.dip = self.add(npyscreen.MultiSelect, name = "Door", max_width=15, relx = 4, rely = 10, max_height=4, value = [], values = ["DOOR"], scroll_exit=True)

	self.dip = self.add(npyscreen.MultiSelect, name = "DIP Switch", max_width = 45, rely =3, relx = 30, max_height=10, value = [], values = ["DIP1", "DIP2", "DIP3","DIP4","DIP5","DIP6","DIP7","DIP8"], scroll_exit=True)

	self.nickel= self.add(npyscreen.MiniButton,name="0.05", rely= 3, relx=50)
	self.dime= self.add(npyscreen.MiniButton,name="0.10", relx=50)
	self.quarter= self.add(npyscreen.MiniButton,name="0.25", relx=50)
	self.dollar= self.add(npyscreen.MiniButton,name="1.00", relx=50)

	self.mode= self.add(npyscreen.MiniButton,name="MODE", relx=50)

        self.wStatus1 = self.add(npyscreen.FixedText, value="Last Command", editable=False, relx=2, rely=12)
        self.wStatus1.important = True

        self.wStatus2 = self.add(npyscreen.FixedText, value="", editable=False)

	
	self.date_widget = self.add(npyscreen.FixedText, value=datetime.now().ctime(), editable=False)
        self.date_widget.value = "Hello"
	self.add_handlers({"^T": self.exit_application})
        
	self.sentfield = self.add(npyscreen.TitleText, name = "Sent:", value="", editable=False )
        self.receivedfield = self.add(npyscreen.TitleText, name = "Received:", value="", editable=False )

    def exit_application(self,name):
        self.parentApp.setNextForm(None)
        self.editing = False


class VirtualSnackApp(npyscreen.NPSAppManaged):
    keypress_timeout_default = 1

    def onStart(self):
	self.addForm("MAIN", VirtualSnack, name="Virtual Snack")
	
	# socket code
    	self.CONNECTION_LIST = []    # list of socket clients
    	self.RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    	PORT = 5000

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
                 
                #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(self.RECV_BUFFER)
                    # echo back the client message
                    if data:
			response = 'OK ... ' + data
                        sock.send(response)
			self.sent = response
			self.received = data
                 
                 
                # client disconnected, so remove from socket list
                except:
                    #print "Client (%s, %s) is offline" % addr
                    sock.close()
                    self.CONNECTION_LIST.remove(sock)
                    continue
             

    def onCleanExit(self):
        self.server_socket.close()

if __name__ == "__main__":
    App = VirtualSnackApp()
    App.run()
