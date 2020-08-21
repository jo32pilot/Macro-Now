from DoubleClickWidgets import EditLabelLine, EditLabelKey, \
        EditLabelKeySequence, MacroWidget
from StepConstants import StepEnum, stepImage, stepDescriptor
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QKeySequenceEdit, QComboBox, \
        QHBoxLayout
from util import makeButton

class KeyListWidgetContainer():
    def __init__(self, container):
        self.container = container

    def getContainer(self):
        return self.container

    def sizeHint(self):
        return self.container.sizeHint()

class KeyListWidgetMacro(KeyListWidgetContainer):
    def __init__(self, recorder, listWidget, text, steps=None, time=0,
            keys=None, keyString='', loopNum=0):
        keyEdit = EditLabelKeySequence(recorder, 'Key here')
        editLabel = EditLabelLine(text)
        loopText = QLabel("Loop:")
        loopSelector = QComboBox()
        macroWidget = MacroWidget(listWidget, keyEdit, editLabel, loopSelector,
                time)
        super().__init__(macroWidget)

        if keys:
            # As long as hotkey exists, make sure key sequence
            # is non-empty. There's no meaning behing 'C'. Any
            # key to make sure it's non-empty
            keyEdit.getEditor().setKeySequence('C')

        comboItems = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'Until Hotkey Pressed']
        loopSelector.addItems(comboItems)
        print(loopNum)
        loopSelector.setCurrentIndex(loopNum if loopNum >= 0 else
                len(comboItems) - 1)

        hLayout = QHBoxLayout()
        hLayout.addWidget(editLabel)
        hLayout.addWidget(editLabel.getEditor())
        hLayout.addStretch()
        hLayout.addWidget(keyEdit)
        hLayout.addWidget(keyEdit.getEditor())
        hLayout.addStretch()
        hLayout.addWidget(loopText)
        hLayout.addWidget(loopSelector)
        self.container.setLayout(hLayout)

        self.container.setSteps(steps)
        self.container.setTime(time)
        self.container.setKeys(keys)
        self.container.setKeyString(keyString)

class KeyListWidgetStep(KeyListWidgetContainer):
    def __init__(self, startTime, stepType, data=None, holdTime=0, parent=None):
        super().__init__(QWidget())

        self.stepType = stepType 
        # Placeholder, will be set properly later
        self.valueLayout = None

        # maybe need to cut precision
        validator = QDoubleValidator()
        validator.setDecimals(2)
        self.pressTime = EditLabelLine(str(holdTime))
        self.pressTime.setValidator(validator)
        self.startTime = EditLabelLine(str(startTime))
        self.startTime.setValidator(validator)

        self.savedParent = parent

        # TODO if reloading after pressing back, need to reparse / set parsedSteps in listWidget?
        hLayout = QHBoxLayout()
        self.editable = self._addStepType(hLayout, stepType, data)
        hLayout.addWidget(self.pressTime)
        hLayout.addWidget(self.pressTime.getEditor())
        hLayout.addStretch()
        hLayout.addWidget(self.startTime)
        hLayout.addWidget(self.startTime.getEditor())

        self.container.setLayout(hLayout)

    def getPress(self):
        return self.pressTime

    def getStart(self):
        return self.startTime

    def getEditable(self):
        return self.editable

    def getParsed(self):
        ''' Parses container for data to later serialize / playback.

        Return: A tuple containing the parsed data. The tuple is formatted as
                follows:

                (step_type, type_data, hold_time, start_time)

                where type_data depends on what step_type is. For each of the
                following step types, we have the following data:

                ACTIVE_WAIT:       (None)   No data
                MOUSE_LEFT /
                MOUSE_RIGHT:       (Tuple)  Coordinates of the mouse click
                MOUSE_SCROLL:      (int)    Y direction scroll offset
                MOUSE_LEFT_DRAG /   
                MOUSE_RIGHT_DRAG   (Tuple)  Tuple containing the two tuples. 
                                            The first tuple contains the coordinates
                                            of the mouse before movement.
                                            The second tuple contains the coordinates
                                            where the mouse stopped.
                KEY:               (String) The key clicked


        '''
        textAt = lambda i: self.valueLayout.itemAt(i).widget().text()
        valueAt = lambda i: float(textAt(i))
        data = None
        time = float(self.pressTime.text())
        startTime = float(self.startTime.text())
        if (self.stepType == StepEnum.MOUSE_LEFT or 
                self.stepType == StepEnum.MOUSE_RIGHT):

            data = (valueAt(1), valueAt(4))

        elif self.stepType == StepEnum.MOUSE_SCROLL:
            data = valueAt(1)

        elif self.stepType == StepEnum.MOUSE_LEFT_DRAG or \
                self.stepType == StepEnum.MOUSE_RIGHT_DRAG:
            start = (valueAt(1), valueAt(4))
            end = (valueAt(9), valueAt(12))
            data = (start, end)

        elif self.stepType == StepEnum.KEY:
            data = textAt(0)

        return (self.stepType, data, time, startTime)

            
    def _removeWidget(self, idx, layout):
        toRemove = layout.takeAt(idx).widget()
        layout.removeWidget(toRemove)
        toRemove.setParent(None)

    def _removeButtons(self, amount, layout):
        for i in range(amount):
            self._removeWidget(1, layout)

    def _changeButton(self, newType, origButton, typeButtonLayout, 
            parentLayout, manualEdit=True):
        if manualEdit:
            self._removeButtons(len(StepEnum) - 1, typeButtonLayout)
        origButton.clicked.disconnect()
        newImage = stepImage(newType)
        origButton.setStyleSheet(newImage)
        origButton.clicked.connect(lambda: self._insertOptions(newType, 
                origButton, typeButtonLayout, parentLayout))

    def _changeType(self, oldType, newType, origButton, typeButtonLayout, 
            parentLayout, data=None, manualEdit=True):
        # replace button image and event handler, and remove extra buttons
        self._changeButton(newType, origButton, typeButtonLayout, parentLayout,
                manualEdit=manualEdit)

        # change type descrption
        parentLayout.itemAt(1).widget().setText(stepDescriptor(newType))

        # change type data
        oldIsClick = (oldType == StepEnum.MOUSE_LEFT 
                or oldType == StepEnum.MOUSE_RIGHT)
        newIsClick = (newType == StepEnum.MOUSE_LEFT 
                or newType == StepEnum.MOUSE_RIGHT)

        if not (oldIsClick and newIsClick):
            data = (0, 0) if newIsClick else data
            # index 2 is a spacer
            self._removeWidget(3, parentLayout)
            newWidget = self._getValueWidget(newType, data)[0]
            parentLayout.insertWidget(3, newWidget)

        self.stepType = newType

    def clickToDrag(self, stepType, oldCoords, newCoords):
        hLayout = self.container.layout()
        typeButtonLayout = hLayout.itemAt(0).layout()
        origButton = typeButtonLayout.itemAt(0).widget()
        newType = StepEnum.MOUSE_LEFT_DRAG if stepType == StepEnum.MOUSE_LEFT \
                else StepEnum.MOUSE_RIGHT_DRAG
        self._changeType(stepType, newType, origButton, typeButtonLayout,
                hLayout, (oldCoords, newCoords), manualEdit=False)


    def _insertOptions(self, currType, origButton, typeButtonLayout,
            parentLayout):

        for stepType in StepEnum:
            if currType != stepType:
                button = makeButton(self.savedButton, stepImage(stepType))

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
            
    def _makeCoordText(self,layout, x, y):
            validator = QIntValidator()
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

        elif stepType == StepEnum.MOUSE_LEFT_DRAG or \
                stepType == StepEnum.MOUSE_RIGHT_DRAG:
            self._makeCoordText(containerLayout, str(data[0][0]), 
                    str(data[0][1]))
            containerLayout.addWidget(QLabel(' -> '))
            coords = self._makeCoordText(containerLayout, 
                    str(data[1][0]), str(data[1][1]))
            returnWidgets.append(coords)

        elif stepType == StepEnum.MOUSE_SCROLL:
            scrollWidget = QLabel(f'Y: ')
            yDir = EditLabelLine(str(data))
            yDir.setValidator(QIntValidator())

            containerLayout.addWidget(scrollWidget)
            containerLayout.addWidget(yDir)

            returnWidgets.append(yDir)

        elif stepType == StepEnum.KEY:
            editDisp = data if data else 'Key Here'
            editLabelKS = EditLabelKey(editDisp)
            containerLayout.addWidget(editLabelKS)
            containerLayout.addWidget(editLabelKS.getEditor())
        elif stepType == StepEnum.ACTIVE_WAIT:
            # placeholder to take space
            containerLayout.addWidget(QWidget())

        self.valueLayout = containerLayout
        typeContainer.setLayout(containerLayout)
        typeContainer.setMinimumWidth(100)

        return returnWidgets

    def _addStepType(self, layout, stepType, data):
        #TODO make editlabel editors smaller because right now taking too much space
        #TODO put cap on number that can be entered. see if can get monitor resolution

        # when change step type, just change image and reconnect onclick
        stepButton = makeButton(self.savedParent, stepImage(stepType))
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

        return valueWidgets[1] if len(valueWidgets) > 1 else None
        
