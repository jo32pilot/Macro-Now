from win32gui import PostQuitMessage
from StepConstants import StepEnum
from pynput import mouse, keyboard
from threading import Thread, Lock
import time

# maybe can turn this all into snake case?

# TODO clean up, put each type in own class

# TODO for mouse move and scroll only change time for time that user moves

class KeyWatcher():

    def __init__(self, listWidget, totalTime):
        self.listWidget = listWidget
        self.totalTime = totalTime
        self.keysDown = dict()

        self.listWidget.keyPress.connect(self.onPress)
        self.listWidget.keyRelease.connect(self.onRelease)
        self.listWidget.mousePress.connect(self.onClick)
        self.listWidget.mouseMove.connect(self.onMouseMove)
        self.listWidget.mouseScroll.connect(self.onScroll)
        self.listWidget.wait.connect(self.onWait)

        self.updater = Thread()
        self.lock = Lock()
        self.startUpdater()

        self.keyController = keyboard.Controller()
        self.mouseController = mouse.Controller()

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

    def onMouseMoveEmit(self, x, y):
        self.listWidget.mouseMove.emit(x, y)

    def onScrollEmit(self, x, y, dx, dy):
        self.listWidget.mouseScroll.emit(x, y, dx, dy)

    def onWaitEmit(self):
        self.listWidget.wait.emit()

    def onRelease(self, key):
        self._dictDel(key)

    def onClick(self, x, y, button, pressed):
        stepType = StepEnum.MOUSE_LEFT if mouse.Button.left else \
                StepEnum.MOUSE_RIGHT
        if pressed:
            press = self.listWidget.listWidgetAddStep(
                    stepType, (x, y)).getPress()
            self._dictAdd(button, (press, time.time()))
        else:
            self._dictDel(button)

    def onWait(self):
        # TODO might need to sync this
        if len(self.keysDown) == 0:
            press = self.listWidget.listWidgetAddStep(
                    StepEnum.ACTIVE_WAIT, None).getPress()
            self._dictAdd(StepEnum.ACTIVE_WAIT, (press, time.time()))
        elif StepEnum.ACTIVE_WAIT in self.keysDown and len(self.keysDown) > 1:
            self._dictDel(StepEnum.ACTIVE_WAIT)


    def startUpdater(self):
        if not self.updater.is_alive():
            self.updater = Thread(target=self.update)
            self.updater.start()

    @synchronize(self.lock)
    def _updateTime(self):
        for key, timeTup in self.keysDown.items():
            if not (key == StepEnum.MOUSE_MOVE or key == StepEnum.MOUSE_SCROLL):
                timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))

    def update(self):
        while True:
            if StepEnum.MOUSE_SCROLL in self.keysDown:
                self._updateScroll()
            if StepEnum.MOUSE_MOVE in self.keysDown:
                self._updateMove()
            self.onWaitEmit()
            self._updateTime()
            time.sleep(.1)


    #TODO do I still even need this?
    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()
