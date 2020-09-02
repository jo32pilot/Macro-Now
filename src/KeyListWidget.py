"""File containing the main list widget class."""

from KeyListWidgetContainer import KeyListWidgetMacro, KeyListWidgetStep
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from StepConstants import StepEnum

class KeyListWidget(QListWidget):
    """Class to extend the functionality of QListWidget.

    The two types of items displayed are macros and steps for each macro.

    Some of the getters and setters of this class access / manipulate the 
    members of this list widget's instance varaibles.

    Attributes:
        currFocus (MacroWidget): When we're looking at the steps of a macro,
                                 this is the MacroWidget instance that
                                 corresponds to the macro and that was 
                                 double clicked to view the steps.
        macroWidgets (list): List of KeyListWidgetMacro objects. These are later
                             serialized into macroList so we can re-render
                             them if we start viewing the steps of a macro
                             instead.
        macroList (list): List of lists containing the data of each macro. 
                          The data in the lists are as follows:

                          [macro_name, steps, total_time,
                          hotkey_keys, hotkey_string, loop_num]

                          macro_name (str): Name of the macro.
                          steps (list): List of the macro's steps.
                          total_time (float): Total time to run the macro.
                          hotkey_keys (set): Set of KeyCodes which run the macro
                                             when pressed.
                          hotkey_string (str): String representation of the
                                               hotkeys.
                          loop_num (int): Number of times to loop the macro.
         
        stepContainers (list): List of KeyListWidgetStep objects from the
                                currently focused macro.
        parsedSteps (list): List tuples containing the data of steps to perform.
                            for the currently focused macro.
        keyWatcher (KeyWatcher): Macro recorder used throughout the program.
        recorder (Hotkeys): Hotkey recorder used throughout the program.
        currFocusIndex (int): Index of the currently focused index in 
                              macroWidgets.
        loopNum (int): Number of times to loop the currently focused macro.

    Class Attributes:
        keyPress (Signal): Signal for when keys are pressed.
        keyRelease (Signal): Signal for when keys are released.
        mousePress (Signal): Signal for when the mouse is clicked or released.
        mouseScroll (Signal): Signal for when the scroll wheel is scrolled.
        wait (Signal): Signal for when the user isn't doing anything.
    """
    keyPress = pyqtSignal(float, object)
    keyRelease = pyqtSignal(float, object)
    mousePress = pyqtSignal(float, float, float, object, bool)
    mouseScroll = pyqtSignal(float, float, float, float, float)
    wait = pyqtSignal(float)

    # index, stepType, data, time, startTime
    #stepUpdate = pyqtSignal(int, object, object, float, float)
    stepUpdate = pyqtSignal(int, float)

    def __init__(self, parent=None):
        """Initializes instance variables.
        
        Args:
            parent (QWidget): Widget to set as this widget's parent.
        """
        super().__init__(parent=parent)
        self.currFocus = None
        self.macroWidgets = []
        self.macroList = []
        self.stepContainers = []
        self.parsedSteps = []
        self.keyWatcher = None
        self.recorder = None
        self.currFocusIndex = 0
        self.loopNum = 0
        self.stepUpdate.connect(self._stepChange)

    def setKeyWatcher(self, watcher):
        self.keyWatcher = watcher

    def setRecorder(self, recorder):
        self.recorder = recorder
    
    def setRecordTotalTime(self, time):
        """Sets the recordTotalTime member of this list's keyWatcher.
        
        Args:
            time (float): Total time to run the macro.
        """
        self.keyWatcher.setRecordTotalTime(time)
    
    def getLoopNum(self):
        return self.loopNum

    def setLoopNum(self, num):
        self.loopNum = num

    def getCurrFocus(self):
        return self.currFocus

    def setCurrFocus(self, macroWidget):
        self.currFocus = macroWidget

    def getParsedSteps(self):
        return self.parsedSteps

    def setParsedSteps(self, steps):
        self.parsedSteps = steps

    def listWidgetAddEditLabel(self, text):
        """Displays a new macro in the list.

        Args:
            text (str): String to display as the macro name.

        Return: The KeyListWidgetMacro created
        """
        item = QListWidgetItem()
        container = KeyListWidgetMacro(self.recorder, self, text)
        self.macroWidgets.append(container)
        self._finalizeItem(item, container)
        return container

    def listWidgetAddStep(self, startTime, stepType, data=None, holdTime=0):
        """Displays a new macro step in the list.

        Args:
            startTime (float): Time in the macro time frame to begin exectuing
                               this step.
            stepType (StepEnum): Type of this step.
            data (Tuple | float): Data describing how to execute this step. This
                                  depends on what stepType is. More on this in 
                                  KeyListWidgetStep.
            holdTime (float): Time to hold this step for.

        Return: The KeyListWidgetStep created.
        """
        item = QListWidgetItem()
        container = KeyListWidgetStep(len(self.stepContainers), startTime,
                stepType, data, holdTime, parent=self)
        self._finalizeItem(item, container)
        self.stepContainers.append(container)
        return container

    def parseSteps(self):
        """Serializes each of the step widgets in stepContainers.
        
        Once parsed, the tuple containing the step's data will be stored
        into parsedSteps.
        """
        self.parsedSteps = []
        for step in self.stepContainers:
            self.parsedSteps.append(step.getParsed())

    def getMacroList(self, write=False):
        """Returns the serialized macro widgets.
        
        Args:
            write: Whether or not we're using this data to write to a file.
        """
        # If we previously serialized macroWidgets into macroList, just
        # return a copy of the list.
        if self.macroList:
            return list(self.macroList)
        writable = []
        for idx, container in enumerate(self.macroWidgets):
            macro = container.getContainer()

            # if we're not using this data to write to a file, then we're
            # backing up the macros to re-display later. That means we've 
            # double clicked a macro widget to view it's steps. We're going to
            # want to edit this macro's data in macroList, because we use
            # macroList to re-create the MacroWidget instances. So we
            # find the index of the macro in the list to edit later.
            if not write and macro is self.currFocus:
                self.currFocusIndex = idx

            backup = [macro.getMacroName(), macro.getSteps(), macro.getTime(),
                    macro.getKeys(), macro.getKeyString(), macro.getLoopNum()]
            writable.append(backup)
        return writable
        
    def backupMacros(self):
        """Serializes and clears the list of macroWidgets."""
        self.macroList = self.getMacroList()
        self.macroWidgets = []

    def updateMacroList(self, time):
        """Updates the data of the currently focused macro within macroList.

        Args:
            time (float): Total time it takes to run this macro.
        """
        currMacro = self.macroList[self.currFocusIndex] 
        # TODO maybe can phase out self.parsedSteps and just use currMacro[1]?
        currMacro[1] = self.parsedSteps
        currMacro[2] = time

    def reloadMacro(self, name, steps, time, keys, keyString,
            loopNum):
        """Creates and displays a macro widget.

        Args:
            name (str): Name of the macro.
            steps (list): List of the macro's steps.
            time (float): Total time to run the macro.
            keys (set): Set of KeyCodes which run the macro
                        when pressed.
            keyString (str): String representation of the
                             hotkeys.
            loopNum (int): Number of times to loop the macro.
        """
        item = QListWidgetItem()
        container = KeyListWidgetMacro(self.recorder, self, name, steps,
                time, keys, keyString, loopNum)
        self.macroWidgets.append(container)
        self._finalizeItem(item, container)

    def reloadMacroList(self):
        """Re-displays the previously backed up macro widgets."""
        self.clear()
        self.stepContainers = []
        for name, steps, time, keys, keyString, loopNum in self.macroList:
            self.reloadMacro(name, steps, time, keys, keyString, loopNum)
        self.macroList = []
        self.currFocus = None

    def _removeItem(self, idx, dataList, additionalList=None):
        """Removes the item at the passed in index from the list.
        
        Args:
            idx (int): Index of item to remove.
            dataList (list): List containing the data of the widget to remove.
                             The data will be removed from this list as well.
            additionalList (list): Another list to remove data from at the
                                   passed in index.
        """
        if additionalList:
            del additionalList[idx]
        del dataList[idx]
        self.takeItem(idx)

    def removeLast(self):
        """Removes the last step added."""
        self._removeItem(self.count() - 1, self.stepContainers)

    def _insertStep(self, idx, item, dataList, widgetUpdate=False):
        temp = item
        for i in range(idx, len(dataList)):
            temp = dataList[i]
            if widgetUpdate:
                item.getContainer().setIdx(i)
            dataList[i] = item
            item = temp
        dataList.append(temp)


    def onAddPress(self):
        """Callback event for when the add button is pressed.

        When looking at the list of macros, adds a new macro to the bottom
        of the list. When looking at macro steps, adds a new active wait step
        under the currently focused step, or to the bottom if no step is
        focused.
        """

        # If we're looking at macro steps.
        if self.currFocus:
            widgetFocus = self.selectedItems()
            item = QListWidgetItem()

            # Default value for if no step is focused
            idx = self.count()
            startTime = 0

            # If a step is focused
            if widgetFocus:
                idx = self.row(widgetFocus[0])
                startTime = self.parsedSteps[idx][3]

            # Create and display new step
            container = KeyListWidgetStep(idx, startTime, StepEnum.ACTIVE_WAIT,
                    None, 0, parent=self)
            self.insertItem(idx, item)
            self._finalizeItem(item, container)
            
            # Updates list so recording over / reloading these steps later
            # works.
            self._insertStep(idx, container, self.stepContainers,
                    widgetUpdate=True)
            self._insertStep(idx, (StepEnum.ACTIVE_WAIT, None, 0,
                startTime), self.parsedSteps)

            # Update hotkey with new step.
            self.recorder.updateMacroSteps(self.currFocus, self.parsedSteps,
                    self.loopNum)
        else:
            self.listWidgetAddEditLabel('untitled')
        

    def onDeletePress(self):
        """Callback event for when the delete button is pressed.

        Essentially deletes the focused list item.
        """
        widgetFocus = self.selectedItems()
        if not widgetFocus:
            return 

        widgetFocus = widgetFocus[0]
        idx = self.row(widgetFocus)

        # If we're editting the steps of a macro
        if self.currFocus: 
            self._removeItem(idx, self.parsedSteps, self.stepContainers)
            for i in range(idx, len(self.stepContainers)):
                self.stepContainers[i].getContainer().setIdx(i)
            self.recorder.updateMacroSteps(self.currFocus, self.parsedSteps,
                    self.loopNum)
        else:
            hotkeyKeys = self.macroWidgets[idx].getContainer().getKeys()
            self.recorder.removeHotkey(hotkeyKeys)
            self._removeItem(idx, self.macroWidgets)
            
    def _stepChange(self, idx, newStartTime):
        # TODO rest of tuple members
        stepType, data, holdTime, startTime = self.parsedSteps[idx]
        self.parsedSteps[idx] = (stepType, data, holdTime, newStartTime)
        if idx == len(self.parsedSteps) - 1:
            self.currFocus.setTime(newStartTime + holdTime)
        self.recorder.updateMacroSteps(self.currFocus, self.parsedSteps,
                self.loopNum)

    def _finalizeItem(self, item, container):
        """Performs the logic to display the item in the list widget."""
        item.setSizeHint(container.sizeHint())    
        self.addItem(item)
        self.setItemWidget(item, container.getContainer())

