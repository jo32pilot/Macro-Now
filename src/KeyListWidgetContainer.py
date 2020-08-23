"""File containing the widgets that will appear in the list widget.

Note that there are two meanings for the word "container" here (which
is confusing, I know). Sometimes it means the member of KeyListWidgetContainer.
This is the top level widget that contains the rest of the widgets to be
displayed. Other times it refers to KeyListWidgetContainer itself and its
subclasses.
"""

from DoubleClickWidgets import EditLabelLine, EditLabelKey, \
        EditLabelKeySequence, MacroWidget
from StepConstants import StepEnum, stepImage, stepDescriptor
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QKeySequenceEdit, QComboBox, \
        QHBoxLayout
from util import makeButton

class KeyListWidgetContainer():
    """Extremely simple base class for the rest of the widgets containers.
    
    Attributes:
        container (QWidget): The top level widget that will contain all other
                             componenets.
    """
    def __init__(self, container):
        """Initializes instance variables.
        
        Args:
            container (QWidget): The top level widget that will contain all
                                 other components.
        """
        self.container = container

    def getContainer(self):
        return self.container

    def sizeHint(self):
        """Returns the size hint of the container member.
        
        Return (QSize): The size hint of the container memeber. 
        """
        return self.container.sizeHint()

class KeyListWidgetMacro(KeyListWidgetContainer):
    """Container for the macro widgets.

    This is the class used to display each macro (not to be confused with
    displaying a Macro's steps).
    """

    def __init__(self, recorder, listWidget, text, steps=None, time=0,
            keys=None, keyString='', loopNum=0):
        """Gathers and laysout all the components of the macro widget.

        Args:
            recorder (Hotkeys): The hotkey recorder used throughout the program.
            listWidget (QListWidget): The sole list widget of this program. 
                                      Passing this in will not display the
                                      widget in the macro. You must also
                                      add a QListWidgetItem and attatch
                                      the container member to it.
            text (str): Text to display as the name of the macro.
            steps (list): List of steps that this macro runs. More on
                          this in KeyListWidgetStep
            time (float): Total time it takes to run this macro.
            keys (set): Set of KeyCodes that, when pressed, run this macro.
            keyString (str): String representation of keys.
            loopNum (int): Number of times to loop this macro.
        """

        # Initialize widgets that will be displayed in the container widget.
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

        # Initialize combobox options.
        comboItems = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 
                'Until Hotkey Pressed']
        loopSelector.addItems(comboItems)
        loopSelector.setCurrentIndex(loopNum - 1 if loopNum > 0 else
                len(comboItems) - 1)

        # Begin laying everything out
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

        # Set member variables of the container.
        self.container.setSteps(steps)
        self.container.setTime(time)
        self.container.setKeys(keys)
        self.container.setKeyString(keyString)

class KeyListWidgetStep(KeyListWidgetContainer):
    """Container for step widgets.

    This class is used to display an individual step of a macro.

    Attribues:
        stepType (StepEnum): Type of step this object displays.
        valueLayout (QHBoxLayout): Layout containing the widgets that display
                                   this step's data.
        pressTime (EditLabelLine): Editable widget displaying how long this step
                                   is held for.
        startTime (EditLabelLine): Editable widget displaying when this step
                                   was exectued since the start of the macro.
        editable (Object): Widget, or a container (list, tuple, etc.) containing
                           widgets, displaying the data for this step that needs
                           to be edited once the step is finished recording.
                           For example, scrolls steps need to be edited to
                           reflect the current offset.
        savedParent (QWidget): Widget to set as the parent of other widgets
                          created in this class.
    """

    def __init__(self, startTime, stepType, data=None, holdTime=0, parent=None):
        """Gathers and laysout all the components of the step widget.

        Args:
            startTime (float): Time this step was executed since the start of
                               the macro.
            stepType (StepEnum): Type of step this object displays.
            data (Tuple | float): Data to display for this step of type 
                                  stepType.
            holdTime (float): How long this step is held for.
            parent (QWidget): Widget to set as the parent of other widgets
                              created in this class.
        """
        super().__init__(QWidget())

        self.stepType = stepType 
        self.valueLayout = None

        # Init widgets that display start and hold time.
        # TODO maybe need to cut precision
        validator = QDoubleValidator()
        validator.setDecimals(2)
        self.pressTime = EditLabelLine(str(holdTime))
        self.pressTime.setValidator(validator)
        self.startTime = EditLabelLine(str(startTime))
        self.startTime.setValidator(validator)

        self.savedParent = parent

        # Begin laying everything out
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
        """Serializes container to later write to file or playback.

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
                                            The first tuple contains the
                                            coordinates of the mouse before
                                            movement.
                                            The second tuple contains the
                                            coordinates where the mouse stopped.
                KEY:               (String) The key clicked


        """
        # Gets the text of the widget at the passed in index in the valueLayout.
        textAt = lambda i: self.valueLayout.itemAt(i).widget().text()
        # Gets the text of the widget at the passed in index in the valueLayout
        # and returns it as a float.
        valueAt = lambda i: float(textAt(i))

        data = None
        time = float(self.pressTime.text())
        startTime = float(self.startTime.text())

        # Parse the data from the valueWidget.
        # TODO make constants for magic numbers
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
        """Removes the widget at the specified index within layout.

        Args:
            idx (int): Index in the layout of the widget to remove.
            layout (QLayout): Layout to remove the widget from.
        """
        toRemove = layout.takeAt(idx).widget()
        layout.removeWidget(toRemove)
        toRemove.setParent(None)

    def _removeButtons(self, amount, layout):
        """Removes a specified amount of widgets from the specified layout.

        This function starts removing widgets from the second widget in the
        layout (index 1). This was created for the sole purpose of removing
        buttons from the layout of type selector buttons.

        Args:
            amount (int): Number of buttons to remove.
            layout (QLayout): Layout to remove the widgets from.

        """
        for i in range(amount):
            self._removeWidget(1, layout)

    def _changeButton(self, newType, origButton, typeButtonLayout, 
            parentLayout, manualEdit=True):
        """Changes the button of this step on type change.

        Args:
            newType (StepType): New step type to change to.
            origButton (QPushButton): Button to click on if we
                                      want to change the type again.
            typeButtonLayout (QHBoxLayout): Layout containing buttons to change
                                            the step type.
            parentLayout (QHBoxLayout): Layout that contains the
                                        typeButtonLayout.
            manualEdit (bool): Whether or not the step type is changed because
                               the user manually changed it.
        """

        # If the user manually edited the step type, then buttons to choose
        # a different step type were displayed. Upon choosing one, we need to
        # remove the rest.
        if manualEdit:
            self._removeButtons(len(StepEnum) - 1, typeButtonLayout)
        origButton.clicked.disconnect()
        newImage = stepImage(newType)

        # Instead of creating a new button, just change the image and attach
        # a new callback.
        origButton.setStyleSheet(newImage)
        origButton.clicked.connect(lambda: self._insertOptions(newType, 
                origButton, typeButtonLayout, parentLayout))

    def _changeType(self, oldType, newType, origButton, typeButtonLayout, 
            parentLayout, data=None, manualEdit=True):
        """Changes the step type.

        When the type of this step changes, the data displayed is changed
        and 0 initialized.

        Args:
            oldType (StepEnum): Current type of this step.
            newType (StepEnum): Type to change this step to.
            origButton (QPushButton): Button to click on if we
                                      want to change the type again.
            typeButtonLayout (QHBoxLayout): Layout containing buttons to change
                                            the step type.
            parentLayout (QHBoxLayout): Layout that contains the
                                        typeButtonLayout.
            data (Tuple | float): Data to initialize the step with.
            manualEdit (bool): Whether or not the step type is changed because
                               the user manually changed it.
        """
        # replace button image and event handler, and remove extra buttons
        self._changeButton(newType, origButton, typeButtonLayout, parentLayout,
                manualEdit=manualEdit)

        # change type descrption
        parentLayout.itemAt(1).widget().setText(stepDescriptor(newType))

        oldIsClick = (oldType == StepEnum.MOUSE_LEFT 
                or oldType == StepEnum.MOUSE_RIGHT)
        newIsClick = (newType == StepEnum.MOUSE_LEFT 
                or newType == StepEnum.MOUSE_RIGHT)

        # If the previous step type and new step type are both
        # mouse clicks, then there's no need to change the 
        # data (click coordinates).
        if not (oldIsClick and newIsClick):
            data = (0, 0) if newIsClick else data
            # index 2 is a spacer
            self._removeWidget(3, parentLayout)
            newWidget = self._getValueWidget(newType, data)[0]
            parentLayout.insertWidget(3, newWidget)

        self.stepType = newType

    def clickToDrag(self, stepType, oldCoords, newCoords):
        """Converts a mouse click step to a mouse drag step.

        Args:
            stepType (StepEnum): The type of click we are converting from.
            oldCoords (Tuple): Tuple of floats denoting the coordinates of the
                               start of the drag.
            newCoords (Tuple): Tuple of floats denoting the coordinates of the
                               end of the drag.
        """
        hLayout = self.container.layout()
        typeButtonLayout = hLayout.itemAt(0).layout()
        origButton = typeButtonLayout.itemAt(0).widget()
        newType = StepEnum.MOUSE_LEFT_DRAG if stepType == StepEnum.MOUSE_LEFT \
                else StepEnum.MOUSE_RIGHT_DRAG
        self._changeType(stepType, newType, origButton, typeButtonLayout,
                hLayout, (oldCoords, newCoords), manualEdit=False)


    def _insertOptions(self, currType, origButton, typeButtonLayout,
            parentLayout):
        """Creates buttons to change to a specific step type.

        Args:
            currType (StepEnum): Current step type.
            origButton (QPushButton): Button clicked to display type options.
            typeButtonLayout (QHBoxLayout): Layout containing buttons to change
                                            the step type.
            parentLayout (QHBoxLayout): Layout that contains the
                                        typeButtonLayout.
        """
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
            
    def _makeCoordText(self, layout, x, y):
        """Creates widgest to display coordinates.

        Args:
            layout (QLayout): Layout to add these coordinates to.
            x (float): X coordinate.
            y (float): Y coordinate.
        """
        # Init widgets
        validator = QIntValidator()
        xCoord = EditLabelLine(x)
        yCoord = EditLabelLine(y)
        xCoord.setValidator(validator)
        yCoord.setValidator(validator)

        # Lays out widgets
        layout.addWidget(QLabel('('))
        layout.addWidget(xCoord)
        layout.addWidget(xCoord.getEditor())
        layout.addWidget(QLabel(', '))
        layout.addWidget(yCoord)
        layout.addWidget(yCoord.getEditor())
        layout.addWidget(QLabel(')'))
        return (xCoord, yCoord)

    def _getValueWidget(self, stepType, data):
        """Creates and returns widgets displaying the data for a step type.

        Args:
            stepType (StepEnum): Type of step to denote what the value widget
                                 should look like.
            data (Tuple | float): Data to initialize the step with.

        Return: List of widgets. The first widget should always be the 
                widget that will added to the list item widget layout.
                Subsequent widgets are those that need to be edited
                in the key watcher
        """
        # TODO for recording new mouse clicks / scrolls, start by context menu

        typeContainer = QWidget()
        returnWidgets = [typeContainer]
        containerLayout = QHBoxLayout()

        # Get data widget depending on the step type.
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
        """Adds the type change button and type data to the passed in layout.

        Args:
            layout (QHboxLayout): Layout to the type change button and type data
                                  to.
            stepType (StepEnum): Type of this step.
            data (tuple | float): Data to initialize this step with.

        Return: The extra widget from _getValueWidget that needs to be edited
                while recording.
        """
        #TODO make editlabel editors smaller because right now taking too much space
        #TODO put cap on number that can be entered. see if can get monitor resolution

        # Init step type change button and it's layout.
        stepButton = makeButton(self.savedParent, stepImage(stepType))
        typeButtonLayout = QHBoxLayout()
        typeButtonLayout.addWidget(stepButton)
        stepButton.clicked.connect(lambda: self._insertOptions(stepType, 
                stepButton, typeButtonLayout, layout))

        layout.addLayout(typeButtonLayout)
        desc = QLabel(stepDescriptor(stepType))
        desc.setMinimumWidth(100)
        layout.addWidget(desc)
        layout.addStretch()

        # Get and add step type data.
        valueWidgets = self._getValueWidget(stepType, data)
        layout.addWidget(valueWidgets[0])
        layout.addStretch()

        return valueWidgets[1] if len(valueWidgets) > 1 else None
        
