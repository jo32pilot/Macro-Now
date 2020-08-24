"""File containing various utility functions."""

from PyQt5 import QtWidgets, QtCore
from StepConstants import StepEnum, keyConst
from pynput.keyboard import KeyCode
import os


def makeButton(parent, image, name='', x=0, y=0, width=30, height=30):
    """Creates and returns a new button.

    Args:
        parent (QWidget): Widget to set as this button's parent.
        image (str): CSS to display the button's image.
        name (str): Name of this widget.
        x (int): X coordinate in window to place the button
        y (int): Y coordinate in window to place the button
        width (int): Width of the button.
        height (int): Height of the button.

    """
    button = QtWidgets.QPushButton(parent)
    button.setGeometry(QtCore.QRect(x, y, width, height))
    button.setStyleSheet(image)
    button.setText('')
    button.setMinimumSize(width, height)
    if name:
        button.setObjectName(name)
    return button

def synchronize(func):
    """Decorator to call a function synchronously.

    This synchrous call is with respect to what threading lock
    blocks. This threading lock should be a member of the first
    argument passed in of the function to be decorated.

    Args:
        func (func): Function to call synchronously.
    """
    def sync_function(self, *args):
        """Synchronous version of the function passed into the decorator.

        Args:
            *args: Aguments passed into the function being decorated.

        """
        self.lock.acquire()
        func(self, *args)
        self.lock.release()
    return sync_function

def read(filename, listWidget, recorder):
    """Reads in a file containing macro data.

    The read in macro data will also be used to initialize the list widget 
    with macro widgets.

    Args:
        filename (str): Name of the file to read.

    """
    if os.path.exists(filename):
        # TODO when optimizing, remember to open in binary mode for carriadge 
        # returns
        with open(filename, 'r') as toLoad:
            for line in toLoad:
                name, steps, time, keys, keyString, loopNum = line.split('\0\0\0')
                steps = _readSteps(steps)
                keys = _readKeys(keys)
                time = float(time)
                loopNum = int(loopNum)
                listWidget.reloadMacro(recorder, name, steps, time,
                        keys, keyString, loopNum)
                recorder.addHotkey(keys, steps, time, loopNum, recording=False)

def write(filename, listWidget):
    """Write the current macro data to a file.

    Note that we delimit by null terminators because we could be writing
    keys the user presesd, so we shouldn't delimit by any possible keyboard
    character.

    Args:
        filename (str): Name of file to write to.
        listWidget (QListWidget): List widget containing the data to be written.
    """
    # maybe write to multiple files for each macro?
    with open(filename, 'w') as out:
        writable = listWidget.getMacroList(write=True)

        # Output buffer
        lines = []
        for toWrite in writable:
            name, steps, time, keys, keyString, loopNum = toWrite
            steps = _serializeSteps(steps) if steps else steps

            # Delimit each hotkey key with a single null terminator
            keys = '\0'.join(map(lambda key: str(key), keys))

            lines.append(f'{name}\0\0\0{steps}\0\0\0{time}\0\0\0{keys}\0\0\0{keyString}\0\0\0{loopNum}\n')
        out.writelines(lines)

def _serializeSteps(steps):
    """Converts each step in the passed in list of steps to a string.

    Each component of the step is delimited by a null terminator.

    Args:
        steps (list): List of tuples containing the data of each step
                      of a macro.

    Return: The passed in steps as a stirng.
    """
    stepsStr = []
    for step in steps:
        stepType, data, hold, startTime = step
        stepType = stepType.value
        stepsStr.append(f'{stepType}\0{data}\0{hold}\0{startTime}')
    return '\0\0'.join(stepsStr)


def _parseData(stepType, dataStr):
    """Parses the passed in data string based on the passed in step type.

    Args:
        stepType (StepEnum): Type of this step to parse data for.
        dataStr (str): String containing the data for this step.

    Return: Parsed data.
    """

    # If the step type is a key press, then let data be the key's string
    # representation.
    data = dataStr
    if stepType == StepEnum.ACTIVE_WAIT:
        data = None
    if stepType == StepEnum.MOUSE_LEFT or stepType == StepEnum.MOUSE_RIGHT:
        x, y = dataStr.split(', ')
        data = (float(x[1:]), float(y[:-1]))
    elif stepType == StepEnum.MOUSE_SCROLL:
        data = float(data)
    elif stepType == StepEnum.MOUSE_LEFT_DRAG or \
            stepType == StepEnum.MOUSE_RIGHT_DRAG:
        startX, startY, endX, endY = dataStr.split(', ')
        # remove parenthesis
        startX = startX[2:]
        startY = startY[:-1]
        endX = endX[1:]
        endY = endY[:-2]
        data = ((float(startX), float(startY)), (float(endX), float(endY)))

    return data

def _readSteps(stepsStr):
    """Takes a string of serialized steps to read.

    Args:
        stepStr (str): String of serialized steps.

    Return: List of steps parsed from the steps string.
    """
    steps = stepsStr.split('\0\0')
    stepsList = []
    for step in steps:
        stepType, data, hold, start = step.split('\0')
        stepType = StepEnum(int(stepType))
        data = _parseData(stepType, data)
        hold = float(hold)
        start = float(start)
        stepsList.append((stepType, data, hold, start))
    return stepsList

def _readKeys(keysStr):
    """Takes a string of serialized hotkey keys to read.

    Args:
        keysStr (str): String of seriealized hotkeys.

    Return: Set of KeyCodes parsed from the keys string.
    """
    keys = keysStr.split('\0')
    keySet = set()

    for key in keys:

        #Special KeyCodes when converted to a string are formatted like
        #KeyCode.<keycode> (e.g. KeyCode.ctrl). So we parse for just <keycode>.
        split = key.split('.')
        if len(split) > 1:
            keySet.add(keyConst(split[1]))

        # Else if virtual key code is surrounded by <>. Need to strip.
        elif key[0] == '<':
            keySet.add(KeyCode.from_vk(int(key[1:-1])))

        # special case where character is a single quote
        else:
            # for some reason key[1:-1] doesn't work
            keySet.add(KeyCode.from_char(key.strip("'")
                    if key != "\"'\"" else "'"))
    return keySet


