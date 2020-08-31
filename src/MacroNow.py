# -*- coding: utf-8 -*-
"""Main driver of this program.

This file contains the logic to display the main window and start
the global hotkeys thread. It also connects many of this program's
classes together.

"""


# Form implementation generated from reading ui file '.\draft1.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from DoubleClickWidgets import MacroWidget, EditLabelKeySequence
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import QtCore, QtGui, QtWidgets
from KeyListWidget import KeyListWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette
from KeyWatcher import KeyWatcher
from win32gui import PumpMessages
from AppConfig import AppConfig
from Hotkeys import Hotkeys
import util

class Ui_MainWindow(QWidget):
    """Class that displays the main application window.""" 

    recordShortcut = pyqtSignal()

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(988, 412)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.listWidget = KeyListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(50, 70, 881, 301))
        self.listWidget.setObjectName("listWidget")

        self.curentTime = QtWidgets.QLCDNumber(self.centralwidget)
        self.curentTime.setGeometry(QtCore.QRect(120, 30, 121, 23))
        self.curentTime.setObjectName("curentTime")
        self.diffTime = QtWidgets.QLCDNumber(self.centralwidget)
        self.diffTime.setGeometry(QtCore.QRect(280, 30, 121, 23))
        self.diffTime.setObjectName("diffTime")
        self.addButton = QtWidgets.QPushButton(self.centralwidget)
        self.addButton.setGeometry(QtCore.QRect(650, 30, 30, 30))
        self.addButton.setStyleSheet("image: url(:/images/images/plus.png);\n"
                "padding:3px;")
        self.addButton.setText("")
        self.addButton.setObjectName("addButton")
        self.undoButton = QtWidgets.QPushButton(self.centralwidget)
        self.undoButton.setGeometry(QtCore.QRect(750, 30, 30, 30))
        self.undoButton.setStyleSheet("image: url(:/images/images/undo.png);\n"
                "padding: 4px;")
        self.undoButton.setText("")
        self.undoButton.setObjectName("undoButton")
        self.redoButton = QtWidgets.QPushButton(self.centralwidget)
        self.redoButton.setGeometry(QtCore.QRect(800, 30, 30, 30))
        self.redoButton.setStyleSheet("image: url(:/images/images/redo.png);\n"
                "padding: 4px;")
        self.redoButton.setText("")
        self.redoButton.setObjectName("redoButton")
        self.configButton = QtWidgets.QPushButton(self.centralwidget)
        self.configButton.setGeometry(QtCore.QRect(900, 30, 30, 30))
        self.configButton.setStyleSheet(
                "image: url(:/images/images/settings.png);\npadding: 3px;")
        self.configButton.setText("")
        self.configButton.setObjectName("configButton")
        self.deleteButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteButton.setGeometry(QtCore.QRect(700, 30, 30, 30))
        self.deleteButton.setStyleSheet(
                "image: url(:/images/images/minus.png);\npadding: 4px;")
        self.deleteButton.setText("")
        self.deleteButton.setObjectName("deleteButton")
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(850, 30, 30, 30))
        self.saveButton.setStyleSheet("image: url(:/images/images/save.png);\n"
                "padding: 4px;")
        self.saveButton.setText("")
        self.saveButton.setObjectName("saveButton")
        self.totalTime = QtWidgets.QLCDNumber(self.centralwidget)
        self.totalTime.setGeometry(QtCore.QRect(440, 30, 121, 23))
        self.totalTime.setObjectName("totalTime")

        self.recordButton = QtWidgets.QPushButton(self.centralwidget)
        self.recordButton.setGeometry(QtCore.QRect(600, 30, 30, 30))
        self.recordButton.setStyleSheet("padding:5px;\n"
                "image: url(:/images/images/record.png);")
        self.recordButton.setText("")
        self.recordButton.setObjectName("recordButton")
        self.recordButton.setCheckable(True)

        self.backButton = QtWidgets.QPushButton(self.centralwidget)
        self.backButton.setGeometry(QtCore.QRect(50, 30, 30, 30))
        self.backButton.setStyleSheet("padding:3px;\n"
                "image: url(:/images/images/back.png);")
        self.backButton.setText("")
        self.backButton.setObjectName("backButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))   

    def backButtonEvent(self, watcher, recorder):
        """Function to run upon clicking the back button.

        Args:
            watcher (KeyWatcher): Macro recorder used throughout the program.
            recorder (Hotkeys): Hotkey recorder used throughout the program.
        """
        # Disable / enable buttons that shouldn't / should be pressed when
        # displaying macros.
        ui.addButton.setDisabled(False)
        ui.backButton.setDisabled(True)
        ui.recordButton.setDisabled(True)

        # Re-display macros
        self.listWidget.reloadMacroList(recorder)
        watcher.onBack()

    def configEvent(self):
        # TODO
        self.configWindow = AppConfig()
        self.configWindow.show()
        
    def onRecordShortcut(self, recorder):
        """Starts recording a macro when the record shortcut is pressed.

        Recording will only begin if we are focusing a specific macro 
        (i.e., when the list of steps is being displayed for a macro).

        """
        # TODO
        # If the list widget doesn't have a macro to focus,
        # then we're looking at the list of macros.
        if not self.listWidget.getCurrFocus():
            return
        self.recordButton.toggle()

    def toggleRecordingWindow(self):
        if self.recordButton.isChecked():
            self.recordMesg = QLabel('Recording')
            self.recordMesg.move(0, 0)
            self.recordMesg.show()
        elif self.recordMesg:
            self.recordMesg.close()



import qtresources_rc


if __name__ == "__main__":
    import sys

    # File to save macros to and read from
    OUT_FILE = 'macros_file'


    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    MacroWidget.ui = ui

    watcher = KeyWatcher(ui.listWidget, ui.totalTime)
    hotkeyRecorder = Hotkeys(watcher)
    AppConfig.setUpClass(hotkeyRecorder, ui)
    AppConfig.readConfig()

    ui.recordShortcut.connect(
            lambda: ui.onRecordShortcut(hotkeyRecorder))
    ui.listWidget.setKeyWatcher(watcher)

    # pass in config here too
    util.read(OUT_FILE, ui.listWidget, hotkeyRecorder)

    ui.recordButton.toggled.connect(watcher.toggleRecord)
    ui.recordButton.toggled.connect(ui.toggleRecordingWindow)
    ui.backButton.clicked.connect(lambda: ui.backButtonEvent(watcher,
            hotkeyRecorder))

    # lmao what is this line
    ui.addButton.clicked.connect(
            lambda: ui.listWidget.listWidgetAddEditLabel(
            hotkeyRecorder, 'untitled'))

    ui.deleteButton.clicked.connect(
            lambda: ui.listWidget.onDeletePress(hotkeyRecorder))

    ui.saveButton.clicked.connect(lambda: util.write(OUT_FILE, ui.listWidget))

    ui.configButton.clicked.connect(lambda: ui.configEvent())

    # Disable buttons that shouldn't be pressed when displaying macros.
    ui.backButton.setDisabled(True)
    ui.recordButton.setDisabled(True)

    #ui.undoButton.clicked.connect(watcher.runMacro)
    #PumpMessages()

    sys.exit(app.exec_())
