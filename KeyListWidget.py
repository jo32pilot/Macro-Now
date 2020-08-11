from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from DoubleClickWidgets import EditLabelLine, EditLabelKeySequence, MacroWidget
from StepConstants import StepEnum, stepImage, stepDescriptor
from PyQt5.QtGui import QDoubleValidator
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
        container = MacroWidget(self)

        editLabel = EditLabelLine(text)

        hLayout = QHBoxLayout()
        hLayout.addWidget(editLabel)
        hLayout.addWidget(editLabel.getEditor())
        hLayout.addWidget(QKeySequenceEdit())

        self._finalizeContainer(item, container, hLayout)

    def listWidgetAddStep(self, stepType, data=None, total=None):
        '''
        
        Return: List of widgets that need to be editted in the key watcher.
                The first element in the list needs to be the hold time widget.
        '''
        item = QListWidgetItem()
        container = QWidget()

        # maybe need to cut precision
        validator = QDoubleValidator()
        validator.setDecimals(2)
        pressTime = EditLabelLine('0')
        pressTime.setValidator(validator)
        #pressTime.setMinimumWidth()
        totalTime = EditLabelLine(str(total))
        totalTime.setValidator(validator)
        #totalTime.setMinimumWidth(100)

        hLayout = QHBoxLayout()
        valueWidgets = self._addStepType(hLayout, stepType, data)
        hLayout.addWidget(pressTime)
        hLayout.addWidget(pressTime.getEditor())
        hLayout.addStretch()
        hLayout.addWidget(totalTime)
        hLayout.addWidget(totalTime.getEditor())

        self._finalizeContainer(item, container, hLayout)
        return [pressTime, *valueWidgets]

    def _makeButton(self, image, name='', x=0, y=0, width=30, height=30):
        button = QtWidgets.QPushButton(self.savedParent)
        button.setGeometry(QtCore.QRect(x, y, width, height))
        button.setStyleSheet(image)
        button.setText('')
        button.setMinimumSize(width, height)
        if name:
            button.setObjectName(name)
        return button

    def _finalizeContainer(self, item, container, layout):
        layout.addStretch()
        container.setLayout(layout)  
        item.setSizeHint(container.sizeHint())    

        self.addItem(item)
        self.setItemWidget(item, container)

    def _makeCoordText(self,layout, x, y):
            validator = QDoubleValidator()
            xCoord = EditLabelLine(x)
            yCoord = EditLabelLine(y)
            xCoord.setValidator(validator)
            yCoord.setValidator(validator)

            layout.addWidget(QLabel('('))
            layout.addWidget(xCoord)
            layout.addWidget(xCoord.getEditor())
            layout.addWidget(QLabel(', '))
            layout.addWidget(yCoord)
            layout.addWidget(yCoord.getEditor())
            layout.addWidget(QLabel(')'))
            return (xCoord, yCoord)

    def _getValueWidget(self, stepType, data):
        '''

        Return: List of widgets. The first widget should always be the 
                widget that will added to the list item widget layout.
                Subsequent widgets are those that need to be edited
                in the key watcher
        '''
        # TODO for recording new mouse clicks / scrolls, start by context menu

        # TODO move value / data to parent layout to make look better

        typeContainer = QWidget()
        returnWidgets = [typeContainer]
        containerLayout = QHBoxLayout()

        if stepType == StepEnum.MOUSE_LEFT or stepType == StepEnum.MOUSE_RIGHT:
            self._makeCoordText(containerLayout, str(data[0]), str(data[1]))

        elif stepType == StepEnum.MOUSE_MOVE:
            self._makeCoordText(containerLayout, str(data[0][0]), 
                    str(data[0][1]))
            containerLayout.addWidget(QLabel(' -> '))
            xCoord, yCoord = self._makeCoordText(containerLayout, 
                    str(data[1][0]), str(data[1][1]))
            returnWidgets.append(xCoord)
            returnWidgets.append(yCoord)

        elif stepType == StepEnum.MOUSE_SCROLL:
            yDir = EditLabelLine(str(data))
            yDir.setValidator(QDoubleValidator())

            scrollWidget = QLabel(f'Y: {data}')
            returnWidgets.append(scrollWidget)

            containerLayout.addWidget(scrollWidget)
            containerLayout.addWidget(yDir)

        elif stepType == StepEnum.KEY:
            edit_disp = data if data else 'Key Here'
            editLabelKS = EditLabelKeySequence(edit_disp)
            containerLayout.addWidget(editLabelKS)
            containerLayout.addWidget(editLabelKS.getEditor())
        elif stepType == StepEnum.ACTIVE_WAIT:
            # placeholder to take space
            containerLayout.addWidget(QWidget())

        typeContainer.setLayout(containerLayout)
        typeContainer.setMinimumWidth(100)

        return returnWidgets

    def _addStepType(self, layout, stepType, data):
        #TODO make editlabel editors smaller because right now taking too much space
        #TODO put cap on number that can be entered. see if can get monitor resolution

        # when change step type, just change image and reconnect onclick
        stepButton = self._makeButton(stepImage(stepType))
        typeButtonLayout = QHBoxLayout()
        typeButtonLayout.addWidget(stepButton)
        stepButton.clicked.connect(lambda: self._insertOptions(stepType, 
                stepButton, typeButtonLayout, layout))

        layout.addLayout(typeButtonLayout)
        desc = QLabel(stepDescriptor(stepType))
        #desc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        desc.setMinimumWidth(100)
        layout.addWidget(desc)
        layout.addStretch()

        valueWidgets = self._getValueWidget(stepType, data)
        layout.addWidget(valueWidgets[0])
        layout.addStretch()

        return valueWidgets[1:]
        

    def _removeWidget(self, idx, layout):
        toRemove = layout.takeAt(idx).widget()
        layout.removeWidget(toRemove)
        toRemove.setParent(None)

    def _removeButtons(self, amount, layout):
        for i in range(amount):
            self._removeWidget(1, layout)

    def _changeButton(self, newType, origButton, typeButtonLayout, 
            parentLayout):
        self._removeButtons(len(StepEnum) - 1, typeButtonLayout)
        origButton.clicked.disconnect()
        newImage = stepImage(newType)
        origButton.setStyleSheet(newImage)
        origButton.clicked.connect(lambda: self._insertOptions(newType, 
                origButton, typeButtonLayout, parentLayout))


    def _changeType(self, oldType, newType, origButton, typeButtonLayout, 
            parentLayout):
        # replace button image and event handler, and remove extra buttons
        self._changeButton(newType, origButton, typeButtonLayout, parentLayout)

        # change type descrption
        parentLayout.itemAt(1).widget().setText(stepDescriptor(newType))

        # change type data
        oldIsClick = (oldType == StepEnum.MOUSE_LEFT 
                or oldType == StepEnum.MOUSE_RIGHT)
        newIsClick = (newType == StepEnum.MOUSE_LEFT 
                or newType == StepEnum.MOUSE_RIGHT)

        if not (oldIsClick and newIsClick):
            data = (0, 0) if newIsClick else None
            # index 2 is a spacer
            self._removeWidget(3, parentLayout)
            newWidget = self._getValueWidget(newType, data)[0]
            parentLayout.insertWidget(3, newWidget)

    def _insertOptions(self, currType, origButton, typeButtonLayout,
            parentLayout):

        for stepType in StepEnum:
            if currType != stepType:
                button = self._makeButton(stepImage(stepType))

                # don't know why I can't just pass in stepType into
                # changeType directly instead of using a keyword arg
                # in the lambda, but it won't work otherwise
                event = lambda ch, stepType=stepType: self._changeType(currType,
                        stepType, origButton, typeButtonLayout, parentLayout)

                button.clicked.connect(event)
                typeButtonLayout.addWidget(button)

        # if same type is clicked, remove added buttons and reconnect 
        # _insertOptions event
        origButton.clicked.disconnect()
        origButton.clicked.connect(lambda: self._changeButton(currType, 
                origButton, typeButtonLayout, parentLayout))
            
