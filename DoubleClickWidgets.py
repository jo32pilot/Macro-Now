from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit

class EditLabel(QLabel):
    def __init__(self, defaultText='', parent=None):
        super().__init__(defaultText, parent=parent)
        self.text = defaultText
        self.lineEdit = QLineEdit()
        self.lineEdit.hide()
        self.lineEdit.returnPressed.connect(lambda: self.updateText())

    def getLineEdit(self):
        return self.lineEdit

    def updateText(self):
        new_text = self.lineEdit.text()
        if new_text:
            self.text = new_text
            self.setText(new_text)
        self.lineEdit.hide()
        self.show()

    def setValidator(self, validator):
        self.lineEdit.setValidator(validator) 

    def mouseDoubleClickEvent(self, event):
        self.lineEdit.setText(self.text)
        self.hide()
        self.lineEdit.show()
        self.lineEdit.setFocus()


class MacroWidget(QWidget):
    def __init__(self, listWidget, parent=None):
        """ 
        
        Args:
            shortcut: Key to press to run macro
            steps: Steps that the macro will simulate
        
        """
        super().__init__(parent)
        self.listWidget = listWidget

    def mouseDoubleClickEvent(self, event):
        print('double click macro widget')
        self.listWidget.clear()


