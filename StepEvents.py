from StepConstants import StepEnum
from util import synchronize
from pynput import mouse
import time

class StepEvent():
    def __init__(self, listWidget, keysDown, lock):
        self.listWidget = listWidget
        self.keysDown = keysDown
        self.lock = lock

    @synchronize
    def _dictAdd(self, key, val):
        self.keysDown[key] = val

    @synchronize
    def _dictDel(self, key):
        timeTup = self.keysDown.get(key, None)
        if timeTup != None:
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            del self.keysDown[key]


class KeyboardEvent(StepEvent):
    def _parseKey(self, key):
        key = str(key)
        # special case where character is a single quote
        key = key.strip("'") if key != "\"'\"" else "'"
        return key if len(key) == 1 else key.split('.')[1]

    def onPress(self, startTime, key):
        if key not in self.keysDown:
            # when start recording, set self.currentTime to 0 and 
            # set start time
            press = self.listWidget.listWidgetAddStep(
                    startTime, StepEnum.KEY, self._parseKey(key)).getPress()
            self._dictAdd(key, (press, time.time()))

    def onRelease(self, startTime, key):
        self._dictDel(key)

class ClickEvent(StepEvent):
    def onClick(self, startTime, x, y, button, pressed):
        stepType = StepEnum.MOUSE_LEFT if button == mouse.Button.left else \
                StepEnum.MOUSE_RIGHT
        if pressed:
            press = self.listWidget.listWidgetAddStep(
                    startTime, stepType, (x, y)).getPress()
            self._dictAdd(button, (press, time.time()))
        else:
            self._dictDel(button)

class WaitEvent(StepEvent):
    def onWait(self, startTime):
        # TODO might need to sync this
        if len(self.keysDown) == 0:
            press = self.listWidget.listWidgetAddStep(
                    startTime, StepEnum.ACTIVE_WAIT, None).getPress()
            self._dictAdd(StepEnum.ACTIVE_WAIT, (press, time.time()))
        elif StepEnum.ACTIVE_WAIT in self.keysDown and len(self.keysDown) > 1:
            self._dictDel(StepEnum.ACTIVE_WAIT)

class ReleaselessEvent(StepEvent):
    def __init__(self, data, listWidget, keysDown, lock):
        super().__init__(listWidget, keysDown, lock)
        self.reset(data)

    def reset(self, data):
        self.data = data
        self.stopStart = 0
        self.stopDelta = 0
        self.endPosWidget = None
        self.check = False

    def _onEvent(self, startTime, stepType, data, increment=False):
        if stepType not in self.keysDown:
            defaultData = self.data if increment else [self.data, data]
            container = self.listWidget.listWidgetAddStep(
                    startTime, stepType, defaultData)

            press = container.getPress()
            self.endPosWidget = container.getEditable()
            self.stopStart = time.time()

            self._dictAdd(stepType, (press, time.time()))
        else:
            if increment:
                self.data += data
            else:
                self.data = data
            self.stopStart = time.time()
            self.check = True

    def _update(self, stepType, updateFunc, reset=False):
        # TODO make configurable
        if self.stopDelta >= 1 and self.endPosWidget != None:
            self.stopDelta = 0
            if reset:
                self.data = 0
            self._dictDel(stepType)
            self.endPosWidget = None
        elif not self.check:
            self.stopDelta = time.time() - self.stopStart
        elif self.check:
            updateFunc()
            timeTup = self.keysDown[stepType]
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            self.check = False

class ScrollEvent(ReleaselessEvent):
    def onScroll(self, startTime, x, y, dx, dy):
        self._onEvent(startTime, StepEnum.MOUSE_SCROLL, dy, increment=True)

    def _updateText(self):
        self.endPosWidget.setText(str(self.data))

    def update(self):
        self._update(StepEnum.MOUSE_SCROLL, self._updateText, reset=True)

class MoveEvent(ReleaselessEvent):
    def onMove(self, startTime, x, y):
        coords = (x, y)
        self._onEvent(startTime, StepEnum.MOUSE_MOVE, coords)

    def _updateText(self):
        x, y = self.data
        self.endPosWidget[0].setText(str(x))
        self.endPosWidget[1].setText(str(y))

    def update(self):
        self._update(StepEnum.MOUSE_MOVE, self._updateText)
    
