from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget, QHBoxLayout, QLayout, QSizePolicy

class EditLabel(QLabel):
    def __init__(self, lineEdit, defaultText, parent=None):
        super().__init__(defaultText, parent=parent)
        self.text = defaultText
        self.lineEdit = lineEdit
    
    def mouseDoubleClickEvent(self, event):
        self.lineEdit.setText(self.text)
        self.hide()
        self.lineEdit.show()
        self.lineEdit.setFocus()

