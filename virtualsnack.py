#!/usr/bin/env python
import npyscreen
from datetime import datetime

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


class VirtualSnackApp(npyscreen.NPSAppManaged):
    keypress_timeout_default = 2

    def onStart(self):
	self.addForm("MAIN", VirtualSnack, name="Virtual Snack")


if __name__ == "__main__":
    App = VirtualSnackApp()
    App.run()
