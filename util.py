from PyQt5 import QtWidgets, QtCore


def makeButton(parent, image, name='', x=0, y=0, width=30, height=30):
    button = QtWidgets.QPushButton(parent)
    button.setGeometry(QtCore.QRect(x, y, width, height))
    button.setStyleSheet(image)
    button.setText('')
    button.setMinimumSize(width, height)
    if name:
        button.setObjectName(name)
    return button

def synchronize(func, lock):
    def sync_function(self, *args):
        lock.acquire()
        func(self, *args)
        lock.release()
    return sync_function

