from PyQt5.QtWidgets import QLabel, QWidget

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


