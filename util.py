from PyQt5 import QtWidgets, QtCore
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
                name, steps, time, keys, keyString = line.split(',')
                steps = list(map(lambda step: step.strip("'"),
                    steps.strip('[]').split(', ')))
                self.listWidget.reloadMacro(recorder, name, steps, float(time),
                        keys, keyString)

def write(filename, listWidget):
    print('beginnint write')
    # maybe write to multiple files for each macro?
    with open(filename, 'w') as out:
        writable = listWidget.getWritable()
        lines = []
        for toWrite in writable:
            name, steps, time, keys, keyString = toWrite
            lines.append(f'{name},{steps},{time},{keys},{keyString}')
        out.writelines(lines)

