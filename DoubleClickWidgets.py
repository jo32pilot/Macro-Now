from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit, QKeySequenceEdit

class EditLabel(QLabel):
    def __init__(self, editor, defaultText='', parent=None):
        super().__init__(defaultText, parent=parent)
        #self.setStyleSheet('padding-left: 25px')
        self.setContentsMargins(10, 2, 10, 2)
        self.savedText = defaultText
        self.editor = editor
        self.editor.hide()

    def getEditor(self):
        return self.editor

    def getSavedText(self):
        return self.savedText

    def _updateText(self, newText):
        if newText:
            self.savedText = newText
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
        self.editor.setText(self.savedText)
        self._beginEdit()

class EditLabelKey(EditLabel):
    def __init__(self, defaultText='', parent=None):
        super().__init__(QKeySequenceEdit(), defaultText=defaultText,
                parent=parent)
        self.editor.editingFinished.connect(lambda: self.updateText())

    def updateText(self):
        newText = self.editor.keySequence().toString()
        self._updateText(newText)

    def mouseDoubleClickEvent(self, event):
        self.editor.clear()
        self._beginEdit()

class EditLabelKeySequence(EditLabel):
    # TODO param for existing keys
    def __init__(self, recorder, defaultText='', parent=None):
        super().__init__(QKeySequenceEdit(), defaultText=defaultText,
                parent=parent)
        self.recorder = recorder
        # TODO set this when finish hotkey recording
        self.keys = None
        # TODO set these when finish steps recording
        self.steps = None
        self.time = 0

    def updateText(self):
        newText = self.editor.keySequence().toString()
        self._updateText(newText)

    def _finishEditing(self, keys):
        self.keys = keys
        self.updateText()
        self.setStyleSheet('background-color: transparent')

    def mouseDoubleClickEvent(self, event):
        self.editor.clear()
        self._beginEdit()
        # TODO set variables / display through recordHotKey
        # either by passing in self or passing in function
        # TODO is self.keys dynamically updating if passed into a
        # function like this
        self.recorder.recordHotkey(self.keys, self.steps, self.time,
                self._finishEditing)

class MacroWidget(QWidget):
    def __init__(self, listWidget, keyEdit, editLabel, time, parent=None):
        """ 
        
        Args:
            shortcut: Key to press to run macro
            steps: Steps that the macro will simulate
        
        """
        super().__init__(parent)
        self.listWidget = listWidget
        self.keyEdit = keyEdit
        self.editLabel = editLabel
        self.time = time

    def mouseDoubleClickEvent(self, event):
        if not self.keyEdit.getEditor().keySequence():
            self.keyEdit.setStyleSheet("background-color: #f4c7c3")
            return
        # must set curr focus before backup macros to correctly update macroList
        self.listWidget.setCurrFocus(self)
        self.listWidget.backupMacros()
        self.listWidget.clear()
        if self.getSteps():
            for step in self.getSteps():
                stepType, data, holdTime, startTime = step
                self.listWidget.listWidgetAddStep(startTime, stepType, data,
                        holdTime)
            self.listWidget.setParsedSteps(self.getSteps())
            self.listWidget.setRecordTotalTime(self.time)


    def getSteps(self):
        return self.keyEdit.steps

    def setSteps(self, steps):
        self.keyEdit.steps = steps

    def getKeys(self):
        return self.keyEdit.keys

    def setKeys(self, keys):
        self.keyEdit.keys = keys

    def getKeyString(self):
        return self.keyEdit.getSavedText()

    def setKeyString(self, keyString):
        self.keyEdit._updateText(keyString)

    def getTime(self):
        return self.keyEdit.time

    def setTime(self, time):
        self.keyEdit.time = time

    def getMacroName(self):
        return self.editLabel.getSavedText()

    def getRecorder(self):
        return self.keyEdit.recorder

