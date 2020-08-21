from PyQt5 import QtWidgets, QtCore
from StepConstants import StepEnum, keyConst
from pynput.keyboard import KeyCode
import os


def makeButton(parent, image, name='', x=0, y=0, width=30, height=30):
    button = QtWidgets.QPushButton(parent)
    button.setGeometry(QtCore.QRect(x, y, width, height))
    button.setStyleSheet(image)
    button.setText('')
    button.setMinimumSize(width, height)
    if name:
        button.setObjectName(name)
    return button

def synchronize(func):
    def sync_function(self, *args):
        self.lock.acquire()
        func(self, *args)
        self.lock.release()
    return sync_function

def read(filename, listWidget, recorder):
    if os.path.exists(filename):
        # when optimizing, remember to open in binary mode for carriadge returns
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
    print('beginning write')
    # maybe write to multiple files for each macro?
    with open(filename, 'w') as out:
        writable = listWidget.getMacroList(write=True)
        # Output buffer
        lines = []
        for toWrite in writable:
            name, steps, time, keys, keyString, loopNum = toWrite
            steps = _serializeSteps(steps) if steps else steps
            keys = '\0'.join(map(lambda key: str(key), keys))
            lines.append(f'{name}\0\0\0{steps}\0\0\0{time}\0\0\0{keys}\0\0\0{keyString}\0\0\0{loopNum}\n')
        out.writelines(lines)

def _serializeSteps(steps):
    stepsStr = []
    for step in steps:
        stepType, data, hold, startTime = step
        stepType = stepType.value
        stepsStr.append(f'{stepType}\0{data}\0{hold}\0{startTime}')
    return '\0\0'.join(stepsStr)


def _parseData(stepType, dataStr):
    # if step type is key, then let data be the string
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
    keys = keysStr.split('\0')
    keySet = set()
    for key in keys:
        split = key.split('.')
        if len(split) > 1:
            keySet.add(keyConst(split[1]))
        # else if virtual key code
        elif key[0] == '<':
            keySet.add(KeyCode.from_vk(int(key[1:-1])))
        else:
            # for some reason key[1:-1] doesn't work
            keySet.add(KeyCode.from_char(key.strip("'")
                    if key != "\"'\"" else "'"))
    return keySet


