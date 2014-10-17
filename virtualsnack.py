#!/usr/bin/env python
import npyscreen
from datetime import datetime

# Incorporates code
# from http://www.binarytides.com/python-socket-server-code-example/
# Socket server in python using select function
import socket, select

# for emulator code
import sys
import string

class ContainedMultiSelect(npyscreen.BoxTitle):
    _contained_widget = npyscreen.TitleMultiSelect

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
		self.kpbuttons.append(self.add(npyscreen.MiniButton,name="%d"%keypad, relx = kpx, rely = kpy))
		
	self.reset= self.add(npyscreen.MiniButton,name="RESET",  relx = kpx + 7, rely = kpy)

	self.dip = self.add(npyscreen.MultiSelect, name = "Door", max_width=15, relx = 4, rely = 10, max_height=4, value = [], values = ["DOOR"], scroll_exit=True, value_changed_callback=self.parentApp.when_door_toggled)

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
	self.add_handlers({"^Q": self.exit_application})
        
	self.sentfield = self.add(npyscreen.TitleText, name = "Sent:", value="", editable=False )
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

		self.do_send("# Virtual Snack\n")
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
                    self.CONNECTION_LIST.remove(sock)
                    continue
             

    def onCleanExit(self):
        self.server_socket.close()
    
    # Snack Emulator comms below
    
    def do_send(self, data):
        # Get the list sockets which are ready to be written through select
        read_sockets,write_sockets,error_sockets = select.select([],self.CONNECTION_LIST,[],0.01)
 
        for sock in write_sockets:
		sock.send(data)

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

    def handle_command(self, command):
        command = string.upper(command)
        if string.find(command, "HELP",0) == 0:
            self.do_help()
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


# code below from vvend.py

# FIXME 
# class appgui:
#    def __init__(self):
#        """
#        In this init we are going to display the main
#        serverinfo window
#        """
#        gladefile="vvend.glade"
#        windowname="vvend"
#        self.wTree=gtk.glade.XML (gladefile,windowname)
#        # we only have two callbacks to register, but
#        # you could register any number, or use a
#        # special class that automatically
#        # registers all callbacks. If you wanted to pass
#        # an argument, you would use a tuple like this:
#        # dic = { "on button1_clicked" :
#        #         (self.button1_clicked, arg1,arg2) , ...
#
#        dic = {
#            "on_button1_clicked" : self.keypad_clicked,
#            "on_button2_clicked" : self.keypad_clicked,
#            "on_button3_clicked" : self.keypad_clicked,
#            "on_button4_clicked" : self.keypad_clicked,
#            "on_button5_clicked" : self.keypad_clicked,
#            "on_button6_clicked" : self.keypad_clicked,
#            "on_button7_clicked" : self.keypad_clicked,
#            "on_button8_clicked" : self.keypad_clicked,
#            "on_button9_clicked" : self.keypad_clicked,
#            "on_button10_clicked" : self.keypad_clicked,
#            "on_button11_clicked" : self.keypad_clicked,
#            "on_button11_clicked" : self.keypad_clicked,
#            "on_door_toggled" : self.door_changed,
#            "on_vvend_destroy_event" : self.quit,
#            "on_vvend_delete_event" : self.quit }
#        self.wTree.signal_autoconnect (dic)
#        display = self.wTree.get_widget("label1")
#        label_font = pango.FontDescription('monospace 28')
#        display.modify_font(label_font)
#
#        label_style = display.get_style().copy()
#        fg_color = display.get_colormap().alloc_color('lightgreen')
#        label_style.fg[gtk.STATE_NORMAL] = fg_color
#        display.set_style(label_style)
#
#        w = self.wTree.get_widget("eventbox1")
#        wstyle = w.get_style().copy()
#        bg_color = w.get_colormap().alloc_color('black')
#        wstyle.bg[gtk.STATE_NORMAL] = bg_color
#        w.set_style(wstyle)
#
#        display.set_text("*5N4CK0RZ*")
#
#        self.messageid = None
#
#        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        #s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
##
##    listenhost=""
##    listenport=5150
##    s.bind((listenhost, listenport))
##    # only one connection
##    s.listen(1)
##    s.setblocking(1)
##    #GDK->gtk.gdk in GTK V 2.0
##    id=gtk.input_add(s, gtk.gdk.INPUT_READ, self.handleNewConnection)
#
#        self.server()
#
#
#        return
#
#        def __del__(self):
#            try:
#                self.sock.close()
#                self.sock.shutdown()
#            except:
#                pass
#
#####CALLBACKS

# FIXME
#    def keypad_clicked(self,widget):
#        key = widget.get_label()
#        if key == 'RESET':
#            key = '11'
#        else:
#            key = '0'+key
#        self.do_send('2'+key+' keypress\n')

# FIXME
#    def handleNewConnection(self,source,condition):
#        #source is a socket in GTK v 1 and a fd in version 2
#        conn, addr = source.accept()
#        sys.stdout.write(conn.recv(1))
#        conn.send("bing\n")
#        return gtk.TRUE

# from http://www.pythonbrasil.com.br/moin.cgi/MonitorandoSocketsComPygtk


# FIXME
#    def send(self, data=None, widget=None):
#        text = self.entry.get_text()
#        self.do_send(text)
#        self.entry.set_text('')

        #


# FIXME
#    def server(self):
#
#        # inicializa o servidor
#        port = 5150
#
#        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#        self.sock.bind(('localhost', port))
#        self.sock.listen(0)
#        print "listening on ", port
#
#        #
#        #
#
#        self.server_tag = gtk.input_add(self.sock, gtk.gdk.INPUT_READ, self.accept)
#
#        # mantemos uma lista dos clientes conectados
#
#        self.clients = {}

# FIXME
#    def accept(self, source, condition):
#
#        #
#        # esperando para ser aceito
#
#        conn, addr = source.accept()
#        self.insert("%s:%s conectado\n" % addr)
#
#
#        self.do_prompt()
#        self.clients[addr] = (conn, gtk.input_add(conn, gtk.gdk.INPUT_READ, self.write))

# FIXME
#    def write(self, source, condition):

#
#        data = source.recv(1024)
#        if data.strip() == 'bye' or not len(data):
#
#            # se o cliente enviar um ''bye'', desconecte-o :)
#
#            source.close()
#            for addr, (conn, tag) in self.clients.iteritems():
#                if source is conn:
#                    gtk.input_remove(tag)
#                    self.insert('%s:%s desconectado\n' % addr)
#                    del self.clients[addr]
#
#                    self.server_tag = gtk.input_add(self.sock, gtk.gdk.INPUT_READ, self.accept)
#                    break
#        elif data.strip() == 'quit':
#            self.quit()
#        else:
#            for (addr, port), (conn, tag) in self.clients.iteritems():
#                if source is conn:
#                    self.insert('%s:%s >>> %s\n'%(addr, port, data.strip()))
#                    self.handle_command(data.strip())
#                    break
#
#        return gtk.TRUE

# FIXME
#    def insert(self, data):
#        statusbar = self.wTree.get_widget("statusbar1")
#        if self.messageid:
#            statusbar.remove(1, self.messageid)
#        self.messageid=statusbar.push(1,data)
#
#    def quit(self, *args):
#        sys.stdout.write("quiting...\n")
#        gtk.input_remove(self.server_tag)
#        for addr, (conn, tag) in self.clients.iteritems():
#            gtk.input_remove(tag)
#            conn.close()
#        self.sock.close()
#        self.sock.shutdown()
#
#        gtk.mainquit()
#        sys.stdout.write("quit!\n")



