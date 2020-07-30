#Codersarts python Assignment Help by top rated Expert

#If you need any help then contact to codersarts offcial website

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, uic

from pyHook import HookManager
from pyHook import HookConstants
from win32gui import PumpMessages, PostQuitMessage
from pprint import pprint

class Keystroke_Watcher(object):
    def __init__(self):
        self.hm = HookManager()
        self.hm.KeyDown = self.on_keyboard_event
        self.hm.HookKeyboard()


    def on_keyboard_event(self, event):
        print(event.KeyID)
        try:
            if event.KeyID  == ord('E'):
                self.your_method()
        finally:
            return True

    def your_method(self):
        self.new_wind = SubWindow()
        self.new_wind.show()

    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()

class SubWindow(QWidget):
    def __init__(self, parent = None):
        super(SubWindow, self).__init__(parent)
        label = QLabel("Sub Window",  self)

    #def closeEvent(self, event):
    #    event.ignore()

class MainWindow(QWidget):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.keyList = QtWidgets.QListView(self)
        self.keyList.setGeometry(QtCore.QRect(260, 160, 256, 192))
        self.keyList.setObjectName("keyList")
        MainWindow.setCentralWidget(self)

    def openSub(self):
        self.sub = SubWindow()
        self.sub.show()


    def closeEvent(self,event):
        widgetList = QApplication.topLevelWidgets()
        numWindows = len(widgetList)
        if numWindows > 1:
            event.accept()
        else:
            event.ignore()

app = QApplication(sys.argv)
mainWin = MainWindow()
mainWin.show()

watcher = Keystroke_Watcher()
PumpMessages()

sys.exit(app.exec_())

