from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit, QKeySequenceEdit

class EditLabel(QLabel):
    def __init__(self, editor, defaultText='', parent=None):
        super().__init__(defaultText, parent=parent)
        self.text = defaultText
        self.editor = editor
        self.editor.hide()

    def getEditor(self):
        return self.editor

    def _updateText(self, newText):
        if newText:
            self.text = newText
            self.setText(newText)
        self.editor.hide()
        self.show()

    def _beginEdit(self):
        self.hide()
        self.editor.show()
        self.editor.setFocus()


class EditLabelLine(EditLabel):
    def __init__(self, defaultText='', parent=None):
        super().__init__(QLineEdit(), defaultText=defaultText, parent=parent)
        self.editor.returnPressed.connect(lambda: self.updateText())

    def updateText(self):
        newText = self.editor.text()
        self._updateText(newText)

    def setValidator(self, validator):
        self.editor.setValidator(validator) 

    def mouseDoubleClickEvent(self, event):
        self.editor.setText(self.text)
        self._beginEdit()

class EditLabelKeySequence(EditLabel):
    def __init__(self, defaultText='', parent=None):
        super().__init__(QKeySequenceEdit(), defaultText=defaultText, parent=parent)
        self.editor.editingFinished.connect(lambda: self.updateText())

    def updateText(self):
        newText = self.editor.keySequence().toString()
        self._updateText(newText)

    def mouseDoubleClickEvent(self, event):
        self.editor.clear()
        self._beginEdit()

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


