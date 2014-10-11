#!/usr/bin/env python
import npyscreen

class VirtualSnack(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = npyscreen.MultiLineEdit

class VirtualSnackApp(npyscreen.NPSApp):
    def main(self):
        F = VirtualSnack()
        F.wStatus1.value = "Virtual Snack"
        F.wStatus2.value = "Last Command"
        
        F.edit()


if __name__ == "__main__":
    App = VirtualSnackApp()
    App.run()
