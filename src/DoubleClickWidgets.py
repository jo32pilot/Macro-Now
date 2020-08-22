"""Define multiple classes which need to override mouseDoubleClickEvent.

Classes in this file override QWidget's mouseDoubleClickEvent to perform
some new function on top of the widget's normal behavior.

"""

from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit, QKeySequenceEdit

class EditLabel(QLabel):
    """Base class for widgets that can be editted upon double clicking.

    Attributes:
        savedText (str): Current text on display.
        editor (QWidget): Some widget which allows for user edits. These edits
                          should then be displayed upon finishing the edit
                          (however that is defined for the given widget).

    """

    def __init__(self, editor, defaultText='', parent=None):
        """Constructor to initialize attributes and set up widget style.
        
        Args:
            editor (QWidget): Some widget which allows for user edits. These 
                              edits should then be displayed upon finishing the
                              edit (however that is defined for the given
                              widget).
            defaultText (str): Text to be displayed initially.
            parent (QWidget): Widget to set as this widget's parent.

        """
        super().__init__(defaultText, parent=parent)
        self.setContentsMargins(10, 2, 10, 2)
        self.savedText = defaultText
        self.editor = editor
        self.editor.hide()

    def getEditor(self):
        return self.editor

    def getSavedText(self):
        return self.savedText

    def _updateText(self, newText):
        """Updates this label's text with the passed in text.

        Hides the editor and shows this label with the new text.

        Args:
            newText (str): Text

        """
        if newText:
            self.savedText = newText
            self.setText(newText)
        self.editor.hide()
        self.show()

    def _beginEdit(self):
        """Shows the editor widget and hides this label."""
        self.hide()
        self.editor.show()
        self.editor.setFocus()


class EditLabelLine(EditLabel):
    """Class to allow QLabel edits using QLineEdit."""
    def __init__(self, defaultText='', parent=None):
        """Initializes base class and sets up QLineEdit return event."""
        super().__init__(QLineEdit(), defaultText=defaultText, parent=parent)
        self.editor.returnPressed.connect(lambda: self.updateText())

    def updateText(self):
        """Gets text from QLineEdit and updates this label."""
        newText = self.editor.text()
        self._updateText(newText)

    def setValidator(self, validator):
        self.editor.setValidator(validator) 

    def mouseDoubleClickEvent(self, event):
        """Overrided double click event to start QLabel edits."""
        self.editor.setText(self.savedText)
        self._beginEdit()

class EditLabelKey(EditLabel):
    """Class to allow QLabel edits using QKeySequenceEdits."""

    def __init__(self, defaultText='', parent=None):
        """Set up base class and QKeySequenceEdit edit finished event."""
        super().__init__(QKeySequenceEdit(), defaultText=defaultText,
                parent=parent)
        self.editor.editingFinished.connect(lambda: self.updateText())

    def updateText(self):
        """Gets text from QKeySequenceEdit and updates this label."""
        newText = self.editor.keySequence().toString()
        self._updateText(newText)

    def mouseDoubleClickEvent(self, event):
        """Overrided double click event to start QLabel edits."""
        self.editor.clear()
        self._beginEdit()

class EditLabelKeySequence(EditLabel):
    """Class to allow QLabel edits using QKeySequenceEdits.

    This class differs from EditLabelKey in that it is mainly used for
    hotkey recording. It therefore has adds upon EditLabelKey's
    functions.

    Attributes:
        recorder (Hotkeys): Hotkey recording object used throughout the program.
        keys (set): Set of pynput key codes that define the hotkey.
        steps (list): List of tuples containing the data of each macro step. 
                      More details found in KeyListWidgetStep
        time (float): Total time in seconds to run the macro this hotkey maps
                      to.
        loopNum (int): Total times to run this macro. If -1 macro runs until
                       the hotkey is pressed again.
        customFunc (func): Function to run if this class isn't used for
                           recording hotkeys for macros.

    Class Attributes:
        recording (bool): Denotes if any instances of this class are currently
                          recording hotkeys.

    """

    recording = False

    def __init__(self, recorder, defaultText='', customFunc=lambda: None,
            parent=None):
        """Constructor to initialize base class and instance variables.

        Args:
            recorder (Hotkeys): Hotkey recorder used throughout the program.
            defaultText (str): Text to initally display.
            customFunc (func): Function to run of this class isn't used for
                               recording hotkeys for macros.
        """
        super().__init__(QKeySequenceEdit(), defaultText=defaultText,
                parent=parent)
        self.recorder = recorder
        self.keys = None
        self.steps = None
        self.time = 0
        self.loopNum = 0
        self.customFunc = customFunc

    def updateText(self):
        """Gets text from QKeySequenceEdit and updates this label."""
        newText = self.editor.keySequence().toString()
        self._updateText(newText)

    def _finishEditing(self, keys):
        """Updates text, style, and keys member variable.
        
        Args:
            keys (set): Set of KeyCodes that represent this hotkey and which
                        will be set as this instances hotkey.
        """
        self.keys = keys
        self.updateText()
        self.setStyleSheet('background-color: transparent')

    def mouseDoubleClickEvent(self, event):
        """Overrided double click event to start QLabel edits.
        
        This function will also start the hotkey recorders recording thread.
        The QLabel will re-display once the user releases a key.
        """
        if EditLabelKeySequence.recording:
            return
        EditLabelKeySequence.recording = True
        self.editor.clear()
        self._beginEdit()
        self.recorder.recordHotkey(self.keys, self.steps, self.time,
                self.loopNum, self._finishEditing, self.customFunc)

class MacroWidget(QWidget):
    """Widget that represents an individual macro.

    This widget will be added to the sole KeyListWidget of the program.

    Attributes:
        listWidget (KeyListWidget): The sole list widget displayed in the
                                    program.
        keyEdit (EditLabelKeySequence): This macro's hotkey editor.
        editLabel (EditLabelLine): Name editor for this macro.
        loopSelector (QComboBox): Combo box selector to select number of times
                                  this macro loops.
        time (float): Time it takes to run this macro in seconds.

    Class Attributes:
        ui (Ui_MainWindow): Main window of this program.

    """

    ui = None

    def __init__(self, listWidget, keyEdit, editLabel, loopSelector,
            time, parent=None):
        """Initializes instance variables and sets up selector change event.
        
        Getters and setters of this class also get members of the 
        EditLabelKeySequence instance attached to the instance of this class.

        Args:
            listWidget (KeyListWidget): The sole list widget displayed in the
                                        program.
            keyEdit (EditLabelKeySequence): This macro's hotkey editor.
            editLabel (EditLabelLine): Name editor for this macro.
            loopSelector (QComboBox): Combo box selector to select number of
                                      times this macro loops.
            time (float): Time it takes to run this macro in seconds.
            parent (QWidget): QWidget to set as this widget's parent.
        
        """
        super().__init__(parent)
        self.listWidget = listWidget
        self.keyEdit = keyEdit
        self.editLabel = editLabel
        self.loopSelector = loopSelector
        self.loopSelector.currentTextChanged.connect(self._loopNumChanged)
        self.time = time

    def mouseDoubleClickEvent(self, event):
        """Display list of steps for that macro this widget represents."""

        # If this macro has no hotkey mapped to it, highlight hotkey edit
        # and return
        if not self.keyEdit.getEditor().keySequence():
            self.keyEdit.setStyleSheet("background-color: #f4c7c3")
            return

        # Disable certains buttons that shouldn't have functionality when 
        # viewing macro steps
        ui = MacroWidget.ui
        ui.backButton.setEnabled(True)
        ui.recordButton.setEnabled(True)
        ui.addButton.setEnabled(False)

        # Must set curr focus before backup macros to correctly update
        # KeyListWidget's member, macroList
        self.listWidget.setCurrFocus(self)

        # Backup so we can re-display list of macros later
        self.listWidget.backupMacros()

        # Remove macro widgets from list.
        self.listWidget.clear()

        if self.getSteps():

            # Begin displaying macro's steps
            for step in self.getSteps():
                stepType, data, holdTime, startTime = step
                self.listWidget.listWidgetAddStep(startTime, stepType, data,
                        holdTime)
            # Setup appropriate list widget variables to allow for
            # editting of macro
            self.listWidget.setParsedSteps(self.getSteps())
            self.listWidget.setRecordTotalTime(self.time)
            self.listWidget.setLoopNum(self.getLoopNum())

    def _parseLoopNum(self, num):
        """Used to parse loop selector text for number of times."""
        try:
            return int(num)
        except ValueError:
            return -1

    def _loopNumChanged(self, text):
        """Updates macro to loop the passed in number of times."""
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

