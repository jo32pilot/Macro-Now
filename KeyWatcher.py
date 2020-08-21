from StepEvents import KeyboardEvent, ClickEvent, WaitEvent, ScrollEvent
from win32gui import PostQuitMessage
from StepConstants import StepEnum
from pynput import mouse, keyboard
from pynput.keyboard import HotKey
from threading import Thread, Lock
from util import synchronize
import time

# TODO temp
from MacroRunner import MacroRunner

# maybe can turn this all into snake case?

# TODO for mouse move and scroll only change time for time that user moves

class KeyWatcher():


    # TODO when press back button going to want to reset a bunch of these variables
    def __init__(self, listWidget, totalTimeDisp):
        self.listWidget = listWidget
        self.totalTimeDisp = totalTimeDisp
        self.recordStartTime = 0
        self.recordTotalTime = 0
        self.startTime = 0
        self.recording = False
        self.keysDown = dict()
        self.lock = Lock()

        self.keyController = keyboard.Controller()
        self.mouseController = mouse.Controller()

        self.keyboardEvent = KeyboardEvent(listWidget, self.keysDown, self.lock)
        self.clickEvent = ClickEvent(listWidget, self.keysDown, self.lock)
        self.waitEvent = WaitEvent(listWidget, self.keysDown, self.lock)
        self.scrollEvent = ScrollEvent(0, listWidget, self.keysDown, self.lock)
        #self.moveEvent = MoveEvent(self.mouseController.position, listWidget, 
        #        self.keysDown, self.lock)

        self.keyboard = keyboard.Listener(on_press=self.onPressEmit, 
                on_release=self.onReleaseEmit)
        self.mouse = mouse.Listener(on_click=self.onClickEmit,
                #on_move=self.onMouseMoveEmit,
                on_scroll=self.onScrollEmit)

        self.keyboard.start()
        self.mouse.start()

    @synchronize
    def _clearRecordState(self):
        self.keysDown.clear()

    def _runMacro(self, steps, time, loopNum, keys, recorder):
        # if user hits multiple times, stick in queue and start new thread
        # when last finishes. (if thread is alive, queue.put())
        runner = MacroRunner(steps, time, loopNum, self.mouseController, 
                self.keyController, keys, recorder)
        runner.start()

    def setRecordTotalTime(self, time):
        self.recordTotalTime = time

    def onBack(self):
        # only reset recordTotalTime if no longer on same macro, need to reload
        # this when changing macros
        self.setRecordTotalTime(0)

    # TODO on record start, disconnect other macros
    def toggleRecord(self, record):
        if record:
            self.scrollEvent.reset(0)
            #self.moveEvent.reset(self.mouseController.position)

            self.listWidget.keyPress.connect(self.keyboardEvent.onPress)
            self.listWidget.keyRelease.connect(self.keyboardEvent.onRelease)
            self.listWidget.mousePress.connect(self.clickEvent.onClick)
            self.listWidget.wait.connect(self.waitEvent.onWait)
            self.listWidget.mouseScroll.connect(self.scrollEvent.onScroll)
            #self.listWidget.mouseMove.connect(self.moveEvent.onMove)
            self.listWidget.getCurrFocus().getRecorder().backupHotkeys()

            self.recordStartTime = time.time()
            self.recording = True
            self.updater = Thread()
            self.startUpdater()
        else:
            self.listWidget.keyPress.disconnect()
            self.listWidget.keyRelease.disconnect()
            self.listWidget.mousePress.disconnect()
            self.listWidget.wait.disconnect()
            self.listWidget.mouseScroll.disconnect()
            #self.listWidget.mouseMove.disconnect()

            currFocus = self.listWidget.getCurrFocus()
            recorder = currFocus.getRecorder()
            recorder.reloadHotkeys()

            self.listWidget.removeLast()

            self.recording = False
            self._clearRecordState()
            newTotalTime = time.time() - self.recordStartTime
            self.recordTotalTime = (newTotalTime if self.recordTotalTime == 0 
                    else self.recordTotalTime + newTotalTime)

            self.listWidget.parseSteps()
            self.listWidget.updateMacroList(self.recordTotalTime)

            hotkey = currFocus.getKeys()
            idx = recorder.findHotkey(hotkey, recording=False)
            parsedSteps = self.listWidget.getParsedSteps()
            if idx == -1:
                recorder.addHotkey(hotkey, parsedSteps, self.recordTotalTime,
                        self.getLoopNum(), recording=False)
            else:
                recorder.setHotkey(idx, hotkey, parsedSteps,
                        self.recordTotalTime, self.listWidget.getLoopNum(),
                        recording=False)
            currFocus.setSteps(parsedSteps)
            currFocus.setTime(self.recordTotalTime)



    # TODO turn off some functionality when running macro or stop running 
    # macro

    def canonize(func):       
        return lambda self, key: func(self, self.keyboard.canonical(key))

    @canonize
    def onPressEmit(self, key):
        self.listWidget.keyPress.emit(self.startTime, key)

    @canonize
    def onReleaseEmit(self, key):
        self.listWidget.keyRelease.emit(self.startTime, key)

    def onClickEmit(self, x, y, button, pressed):
        self.listWidget.mousePress.emit(self.startTime, x, y, button, pressed)

    def onWaitEmit(self):
        self.listWidget.wait.emit(self.startTime)

    def onScrollEmit(self, x, y, dx, dy):
        self.listWidget.mouseScroll.emit(self.startTime, x, y, dx, dy)

    def onMouseMoveEmit(self, x, y):
        self.listWidget.mouseMove.emit(self.startTime, x, y)

    def startUpdater(self):
        if not self.updater.is_alive():
            self.updater = Thread(target=self._update)
            self.updater.start()

    @synchronize
    def _updateTime(self):
        for key, timeTup in self.keysDown.items():
            if not key == StepEnum.MOUSE_SCROLL:
                timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))

    def _update(self):
        while self.recording:
            self.startTime = time.time() - self.recordStartTime + self.recordTotalTime
            if StepEnum.MOUSE_SCROLL in self.keysDown:
                self.scrollEvent.update()
            self.onWaitEmit()
            self._updateTime()
            time.sleep(.1)

    def shutdown(self):
        PostQuitMessage(0)
        # stop relavent threads?

