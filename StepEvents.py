

class StepEvent():
    def __init__(self, listWidget, keysDown, lock):
        self.listWidget = listWidget
        self.keysDown = keysDown
        self.lock = lock

    @synchronize(self.lock)
    def _dictAdd(self, key, val):
        self.keysDown[key] = val

    @synchronize(self.lock)
    def _dictDel(self, key):
        timeTup = self.keysDown.get(key, None)
        if timeTup != None:
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            del self.keysDown[key]


class PressEvent(StepEvent):
    def event(self, key):
        if key not in self.keysDown:
            # when start recording, set self.currentTime to 0 and 
            # set start time
            press = self.listWidget.listWidgetAddStep(
                    StepEnum.KEY, str(key)).getPress()
            self._dictAdd(key, (press, time.time()))



class ReleaselessEvent(StepEvent):
    def __init__(self, data, listWidget, keysDown):
        super().__init__(listWidget, keysDown)
        self.data = data
        self.stopStart = 0
        self.stopDelta = 0
        self.widget = None
        self.check = False

    def onEvent(self, stepType, data):
        if stepType not in self.keysDown:
            container = listWidget.listWidgetAddStep(
                    stepType, [self.data, initial])

            press = container.getPress()
            self.endPosWidget = container.getEditable()
            self.stopDelta = time.time()

            self._dictAdd(stepType, (press, time.time()))
        else:
            self.data = data
            self.stopStart = time.time()
            self.check = True

    def _update(self, stepType, updateFunc, resetFunc=lambda: pass):
        # TODO make configurable
        if self.stopDelta >= 1 and self.endPosWidget != None:
            self.stopDelta = 0
            resetFunc()
            self._dictDel(stepType)
            self.endPosWidget = None
        elif not self.scrolling:
            self.stopDelta = time.time() - self.stopStart
        elif self.check:
            updateFunc(self)
            timeTup = self.keysDown[stepType]
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            self.check = False

class MoveEvent(ReleaselessEvent)
    def _updateText(self):
        x, y = self.data
        self.endPosWidget[0].setText(str(x))
        self.endPosWidget[1].setText(str(y))

    def update(self):
        self._update(StepEnum.MOUSE_MOVE, self._updateText)
    

class ScrollEvent(ReleaselessEvent):
    def _updateText(self):
        self.endPosWidget.setText(f'Y: {self.data}')

    def update(self):
        self._update(StepEnum.MOUSE_SCROLL, 
                self._updateText, lambda: self.data = 0)

