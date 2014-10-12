#!/usr/bin/env python
import npyscreen
from datetime import datetime

class ContainedMultiSelect(npyscreen.BoxTitle):
    _contained_widget = npyscreen.TitleMultiSelect

class VirtualSnack(npyscreen.Form):

    def while_waiting(self):
        self.date_widget.value = datetime.now()
        self.display()

    def create(self, *args, **keywords):
        super(VirtualSnack, self).create(*args, **keywords)

        self.wStatus1 = self.add(npyscreen.FixedText, value="Last Command", editable=False)


        self.wStatus2 = self.add(npyscreen.FixedText, value="", editable=False)

        self.wStatus1.important = True
	
	self.date_widget = self.add(npyscreen.FixedText, value=datetime.now(), editable=False)
        self.date_widget.value = "Hello"
	self.add_handlers({"^T": self.exit_application})

	self.dip = self.add(npyscreen.MultiSelect, name = "DIP Switch", max_width = 45, relx = 2, max_height=10, value = [], values = ["DIP1", "DIP2", "DIP3","DIP4","DIP5","DIP6","DIP7","DIP8"], scroll_exit=True)
	self.dip = self.add(npyscreen.MultiSelect, name = "Door", max_width=15, relx = 2, max_height=4, value = [], values = ["DOOR"], scroll_exit=True)

	self.nickel= self.add(npyscreen.MiniButton,name="0.05")
	self.dime= self.add(npyscreen.MiniButton,name="0.10")
	self.quarter= self.add(npyscreen.MiniButton,name="0.25")
	self.dollar= self.add(npyscreen.MiniButton,name="1.00")

	self.mode= self.add(npyscreen.MiniButton,name="MODE")
	self.reset= self.add(npyscreen.MiniButton,name="RESET")

	self.kpbuttons = []
	for keypad in range(0,10):
		self.kpbuttons.append(self.add(npyscreen.MiniButton,name="%d"%keypad))
		

    def exit_application(self,name):
        self.parentApp.setNextForm(None)
        self.editing = False


class VirtualSnackApp(npyscreen.NPSAppManaged):
    keypress_timeout_default = 2

    def onStart(self):
	self.addForm("MAIN", VirtualSnack, name="Virtual Snack")


if __name__ == "__main__":
    App = VirtualSnackApp()
    App.run()
