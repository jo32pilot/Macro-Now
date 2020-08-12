from KeyListWidgetContainer import KeyListWidgetMacro, KeyListWidgetStep
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal

class KeyListWidget(QListWidget):

    keyPress = pyqtSignal(object)
    keyRelease = pyqtSignal(object)
    mousePress = pyqtSignal(float, float, object, bool)
    mouseMove = pyqtSignal(float, float)
    mouseScroll = pyqtSignal(float, float, float, float)
    wait = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.savedParent = parent

    def listWidgetAddEditLabel(self, text):
        item = QListWidgetItem()
        container = KeyListWidgetMacro(self, text)
        self._finalizeItem(item, container)

    def listWidgetAddStep(self, stepType, data=None, total=None):
        '''
        
        Return: List of widgets that need to be editted in the key watcher.
                The first element in the list needs to be the hold time widget.
        '''
        item = QListWidgetItem()
        container = KeyListWidgetStep(stepType, data, total, 
                parent=self.savedParent)
        self._finalizeItem(item, container)
        return container

    def _finalizeItem(self, item, container):
        item.setSizeHint(container.sizeHint())    
        self.addItem(item)
        self.setItemWidget(item, container.getContainer())

