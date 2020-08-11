from win32gui import PostQuitMessage
from StepConstants import StepEnum
from pynput import mouse, keyboard
from threading import Thread, Lock
import time

# maybe can turn this all into snake case?

class KeyWatcher():

    def __init__(self, listWidget, totalTime):
        self.listWidget = listWidget
        self.totalTime = totalTime
        self.keysDown = dict()

        self.listWidget.keyPress.connect(self.onPress)
        self.listWidget.keyRelease.connect(self.onRelease)
        self.listWidget.mousePress.connect(self.onClick)
        self.listWidget.mouseMove.connect(self.onMouseMove)

        self.updater = Thread()
        self.lock = Lock()

        self.keyController = keyboard.Controller()
        self.mouseController = mouse.Controller()

        self.pos = self.mouseController.position
        self.moveStopDelta = 0
        self.stopDeltaStart = 0
        self.endPosWidget = None
        self.moving = False

        self.keyboard = keyboard.Listener(on_press=self.onPressEmit, 
                on_release=self.onReleaseEmit)
        self.mouse = mouse.Listener(on_click=self.onClickEmit,
                on_move=self.onMouseMoveEmit)

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

    def onMouseMove(self, x, y):
        if StepEnum.MOUSE_MOVE not in self.keysDown:
            valueWidgets = self.listWidget.listWidgetAddStep(
                    StepEnum.MOUSE_MOVE, [self.pos, (x, y)])

            press, endLabel = valueWidgets[0], valueWidgets[1:]
            self.stopDeltaStart = time.time()

            self._dictAdd(StepEnum.MOUSE_MOVE, (press, time.time()))
            self.endPosWidget = endLabel
            self.startUpdater()
        else:
            self.pos = (x, y)
            self.stopDeltaStart = time.time()
            self.moving = True

    def _updateMove(self):
        x, y = self.pos

        # TODO make the threshold configurable
        if self.moveStopDelta >= 1 and self.endPosWidget != None:
            self.moveStopDelta = 0
            self._dictDel(StepEnum.MOUSE_MOVE)
            self.endPosWidget = None
        elif not self.moving:
            self.moveStopDelta = time.time() - self.stopDeltaStart
        elif self.moving:
            self.endPosWidget[0].setText(str(x))
            self.endPosWidget[1].setText(str(y))

            timeTup = self.keysDown[StepEnum.MOUSE_MOVE]
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            self.moving = False

    def onPress(self, key):
        if key not in self.keysDown:
            # when start recording, set self.currentTime to 0 and 
            # set start time
            press = self.listWidget.listWidgetAddStep(StepEnum.KEY, str(key))[0]
            self._dictAdd(key, (press, time.time()))
            self.startUpdater()


    def onRelease(self, key):
        self._dictDel(key)

    def onClick(self, x, y, button, pressed):
        stepType = StepEnum.MOUSE_LEFT if mouse.Button.left else \
                StepEnum.MOUSE_RIGHT
        if pressed:
            press = self.listWidget.listWidgetAddStep(stepType, (x, y))[0]
            self._dictAdd(button, (press, time.time()))
            self.startUpdater()
        else:
            self._dictDel(button)


    def startUpdater(self):
        if not self.updater.is_alive():
            self.updater = Thread(target=self.update)
            self.updater.start()

    def _synchronize(func):
        def sync_function(self, *args):
            self.lock.acquire()
            func(self, *args)
            self.lock.release()
        return sync_function

    @_synchronize
    def _dictAdd(self, key, val):
        self.keysDown[key] = val

    @_synchronize
    def _dictDel(self, key):
        timeTup = self.keysDown.get(key, None)
        if timeTup != None:
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            del self.keysDown[key]

    @_synchronize
    def _updateTime(self):
        for key, timeTup in self.keysDown.items():
            if not key == StepEnum.MOUSE_MOVE:
                timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))


    def update(self):
        while len(self.keysDown) != 0:
            if StepEnum.MOUSE_MOVE in self.keysDown:
                self._updateMove()
            self._updateTime()
            time.sleep(.05)


    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()

    def start_record_event(self):
        pass
