from KeyListWidgetContainer import KeyListWidgetMacro, KeyListWidgetStep
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal

class KeyListWidget(QListWidget):

    keyPress = pyqtSignal(float, object)
    keyRelease = pyqtSignal(float, object)
    mousePress = pyqtSignal(float, float, float, object, bool)
    mouseMove = pyqtSignal(float, float, float)
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
    
    def getCurrFocus(self):
        return self.currFocus

    def setCurrFocus(self, macroWidget):
        self.currFocus = macroWidget

    def getParsedSteps(self):
        return self.parsedSteps

    def listWidgetAddEditLabel(self, recorder, text):
        item = QListWidgetItem()
        container = KeyListWidgetMacro(recorder, self, text)
        self.macroWidgets.append(container)
        self._finalizeItem(item, container)

    def listWidgetAddStep(self, startTime, stepType, data=None):
        item = QListWidgetItem()
        container = KeyListWidgetStep(startTime, stepType, data, 
                parent=self.savedParent)
        self._finalizeItem(item, container)
        self.stepContainers.append(container)
        return container

    def parseSteps(self):
        self.parsedSteps = []
        for step in self.stepContainers:
            self.parsedSteps.append(step.getParsed())

    def getWritable(self):
        if self.macroList:
            return list(self.macroList)
        writable = []
        for container in self.macroWidgets:
            macro = container.getContainer()
            backup = (macro.getMacroName(), macro.getSteps(), macro.getTime(),
                    macro.getKeys(), macro.getKeyString())
            writable.append(backup)
        return writable
        
    def backupMacros(self):
        self.macroList = self.getWritable()
        self.macroWidgets = []

    def reloadMacroList(self, recorder):
        for name, steps, time, keys, keyString in self.macroList:
            self.reloadMacro(recorder, name, steps, time, keys, keyString)
        self.macroList = []

    def reloadMacro(self, recorder, name, steps, time, keys, keyString):
        item = QListWidgetItem()
        container = KeyListWidgetMacro(recorder, self, name, steps,
                time, keys, keyString)
        self.macroWidgets.append(container)
        self._finalizeItem(item, container)

    def _finalizeItem(self, item, container):
        item.setSizeHint(container.sizeHint())    
        self.addItem(item)
        self.setItemWidget(item, container.getContainer())

