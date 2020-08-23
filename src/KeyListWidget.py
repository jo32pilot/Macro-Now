from KeyListWidgetContainer import KeyListWidgetMacro, KeyListWidgetStep
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal

class KeyListWidget(QListWidget):

    keyPress = pyqtSignal(float, object)
    keyRelease = pyqtSignal(float, object)
    mousePress = pyqtSignal(float, float, float, object, bool)
    mouseScroll = pyqtSignal(float, float, float, float, float)
    wait = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.savedParent = parent
        self.currFocus = None
        self.macroWidgets = []
        self.macroList = []
        self.stepContainers = []
        self.parsedSteps = []
        self.keyWatcher = None
        self.currFocusIndex = 0
        self.loopNum = 0

    def setKeyWatcher(self, watcher):
        self.keyWatcher = watcher
    
    def setRecordTotalTime(self, time):
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

    def listWidgetAddEditLabel(self, recorder, text):
        item = QListWidgetItem()
        container = KeyListWidgetMacro(recorder, self, text)
        self.macroWidgets.append(container)
        self._finalizeItem(item, container)

    def listWidgetAddStep(self, startTime, stepType, data=None, holdTime=0):
        item = QListWidgetItem()
        container = KeyListWidgetStep(startTime, stepType, data, 
                holdTime, parent=self.savedParent)
        self._finalizeItem(item, container)
        self.stepContainers.append(container)
        return container

    def parseSteps(self):
        self.parsedSteps = []
        for step in self.stepContainers:
            self.parsedSteps.append(step.getParsed())

    def getMacroList(self, write=False):
        if self.macroList:
            return list(self.macroList)
        writable = []
        for idx, container in enumerate(self.macroWidgets):
            macro = container.getContainer()
            if not write and macro is self.currFocus:
                self.currFocusIndex = idx
            backup = [macro.getMacroName(), macro.getSteps(), macro.getTime(),
                    macro.getKeys(), macro.getKeyString(), macro.getLoopNum()]
            writable.append(backup)
        return writable
        
    def backupMacros(self):
        self.macroList = self.getMacroList()
        self.macroWidgets = []

    def updateMacroList(self, time):
        currMacro = self.macroList[self.currFocusIndex] 
        # maybe can phase out self.parsedSteps and just use this?
        currMacro[1] = self.parsedSteps
        currMacro[2] = time

    def reloadMacro(self, recorder, name, steps, time, keys, keyString,
            loopNum):
        item = QListWidgetItem()
        container = KeyListWidgetMacro(recorder, self, name, steps,
                time, keys, keyString, loopNum)
        self.macroWidgets.append(container)
        self._finalizeItem(item, container)

    def reloadMacroList(self, recorder):
        self.clear()
        self.stepContainers = []
        for name, steps, time, keys, keyString, loopNum in self.macroList:
            self.reloadMacro(recorder, name, steps, time, keys, keyString,
                    loopNum)
        self.macroList = []

    def removeLast(self):
        del self.stepContainers[-1]
        self.takeItem(self.count() - 1)


    def _finalizeItem(self, item, container):
        item.setSizeHint(container.sizeHint())    
        self.addItem(item)
        self.setItemWidget(item, container.getContainer())
