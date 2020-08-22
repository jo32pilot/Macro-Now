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

    recording = False

    # TODO param for existing keys
    def __init__(self, recorder, defaultText='', parent=None):
        super().__init__(QKeySequenceEdit(), defaultText=defaultText,
                parent=parent)
        self.recorder = recorder
        self.keys = None
        self.steps = None
        self.time = 0
        self.loopNum = 0

    def updateText(self):
        newText = self.editor.keySequence().toString()
        self._updateText(newText)

    def _finishEditing(self, keys):
        self.keys = keys
        self.updateText()
        self.setStyleSheet('background-color: transparent')

    def mouseDoubleClickEvent(self, event):
        if EditLabelKeySequence.recording:
            return
        EditLabelKeySequence.recording = True
        self.editor.clear()
        self._beginEdit()
        self.recorder.recordHotkey(self.keys, self.steps, self.time,
                self.loopNum, self._finishEditing)

class MacroWidget(QWidget):

    ui = None

    def __init__(self, listWidget, keyEdit, editLabel, loopSelector,
            time, parent=None):
        """ 
        
        Args:
            shortcut: Key to press to run macro
            steps: Steps that the macro will simulate
        
        """
        super().__init__(parent)
        self.listWidget = listWidget
        self.keyEdit = keyEdit
        self.editLabel = editLabel
        self.loopSelector = loopSelector
        self.loopSelector.currentTextChanged.connect(self._loopNumChanged)
        self.time = time

    def mouseDoubleClickEvent(self, event):
        if not self.keyEdit.getEditor().keySequence():
            self.keyEdit.setStyleSheet("background-color: #f4c7c3")
            return
        ui = MacroWidget.ui
        ui.backButton.setEnabled(True)
        ui.recordButton.setEnabled(True)
        ui.addButton.setEnabled(False)
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
            self.listWidget.setLoopNum(self.getLoopNum())

    def _parseLoopNum(self, num):
        try:
            return int(num)
        except ValueError:
            return -1

    def _loopNumChanged(self, text):
        num = self._parseLoopNum(text)
        self.setLoopNum(num)
        self.listWidget.setLoopNum(num)
        idx = self.getRecorder().findHotkey(self.getKeys(), recording=False)
        self.getRecorder().setHotkey(idx, self.getKeys(), self.getSteps(),
                self.getTime(), num, recording=False)


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

    def getLoopNum(self):
        return self.keyEdit.loopNum

    def setLoopNum(self, num):
        self.keyEdit.loopNum = num

    def getMacroName(self):
        return self.editLabel.getSavedText()

    def getRecorder(self):
        return self.keyEdit.recorder

