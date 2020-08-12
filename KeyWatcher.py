from StepEvents import KeyboardEvent, ClickEvent, WaitEvent, ScrollEvent, \
        MoveEvent
from win32gui import PostQuitMessage
from StepConstants import StepEnum
from pynput import mouse, keyboard
from threading import Thread, Lock
from util import synchronize
import time

# maybe can turn this all into snake case?

# TODO for mouse move and scroll only change time for time that user moves

class KeyWatcher():

    def __init__(self, listWidget, totalTime):
        self.listWidget = listWidget
        self.totalTime = totalTime
        self.keysDown = dict()
        self.lock = Lock()

        self.keyController = keyboard.Controller()
        self.mouseController = mouse.Controller()

        self.keyboardEvent = KeyboardEvent(listWidget, self.keysDown, self.lock)
        self.clickEvent = ClickEvent(listWidget, self.keysDown, self.lock)
        self.waitEvent = WaitEvent(listWidget, self.keysDown, self.lock)
        self.scrollEvent = ScrollEvent(0, listWidget, self.keysDown, self.lock)
        self.moveEvent = MoveEvent(self.mouseController.position, listWidget, 
                self.keysDown, self.lock)

        self.listWidget.keyPress.connect(self.keyboardEvent.onPress)
        self.listWidget.keyRelease.connect(self.keyboardEvent.onRelease)
        self.listWidget.mousePress.connect(self.clickEvent.onClick)
        self.listWidget.wait.connect(self.waitEvent.onWait)
        self.listWidget.mouseScroll.connect(self.scrollEvent.onScroll)
        self.listWidget.mouseMove.connect(self.moveEvent.onMove)

        self.updater = Thread()
        self.startUpdater()

        self.keyboard = keyboard.Listener(on_press=self.onPressEmit, 
                on_release=self.onReleaseEmit)
        self.mouse = mouse.Listener(on_click=self.onClickEmit,
                on_move=self.onMouseMoveEmit,
                on_scroll=self.onScrollEmit)

        self.keyboard.start()
        self.mouse.start()

    def canonize(func):       
        return lambda self, key: func(self, self.keyboard.canonical(key))

    @canonize
    def onPressEmit(self, key):
        self.listWidget.keyPress.emit(key)

    @canonize
    def onReleaseEmit(self, key):
        self.listWidget.keyRelease.emit(key)

    def onClickEmit(self, x, y, button, pressed):
        self.listWidget.mousePress.emit(x, y, button, pressed)

    def onWaitEmit(self):
        self.listWidget.wait.emit()

    def onScrollEmit(self, x, y, dx, dy):
        self.listWidget.mouseScroll.emit(x, y, dx, dy)

    def onMouseMoveEmit(self, x, y):
        self.listWidget.mouseMove.emit(x, y)

    def startUpdater(self):
        if not self.updater.is_alive():
            self.updater = Thread(target=self.update)
            self.updater.start()

    @synchronize
    def _updateTime(self):
        for key, timeTup in self.keysDown.items():
            if not (key == StepEnum.MOUSE_MOVE or key == StepEnum.MOUSE_SCROLL):
                timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))

    def update(self):
        while True:
            if StepEnum.MOUSE_SCROLL in self.keysDown:
                self.scrollEvent.update()
            if StepEnum.MOUSE_MOVE in self.keysDown:
                self.moveEvent.update()
            self.onWaitEmit()
            self._updateTime()
            time.sleep(.1)

    #TODO do I still even need this?
    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()

