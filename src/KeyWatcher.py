"""This file contains the class that records macros."""

from StepEvents import KeyboardEvent, ClickEvent, WaitEvent, ScrollEvent
from win32gui import PostQuitMessage
from MacroRunner import MacroRunner
from StepConstants import StepEnum
from pynput import mouse, keyboard
from pynput.keyboard import HotKey
from threading import Thread, Lock
from util import synchronize
import time

class KeyWatcher():
    """Class to record macros.

    Upon initializing this class, the keyboard listeners and mouse listeners,
    which are Thread objects, will start.

    Attributes:
        listWidget (KeyListWidget): The sole list widget displayed in the
                                    program.
        totalTimeDisp (QLCDNumber): Widget to display total time this macro
                                    takes.
        recordStartTime (float): Time when macro began recording.
        recordTotalTime (float): Time it took to run the macro
        startTime (float): Current time passed since macro recording 
                           started. Used to denote when we began 
                           recording a step.
        recording (bool): Whether or not we are currently recording a macro.
        keysDown (dict): Mapping of keys currently pressed
                         (or if scrolling / clicking) to a tuple containing
                         their time held display and the time they were 
                         detected.
        lock (Lock): Threading lock to prevent race conditions in the keysDown
                     dict which can happen between the display updater thread
                     and the listener threads.
        keyboardEvent (KeyboardEvent): Class containing event listeners for 
                                       the keyboard.
        clickEvent (ClickEvent): Class containing event listeners for mouse
                                 clicks.
        waitEvent (WaitEvent): Class containg events listeners for when the
                               the user doesn't do anything.
        scrollEvent (ScrollEvent): Class containing event listeners for scroll
                                   events.
        keyboard (Listener): Keyboard listener thread.
        mouse (Listener): Mouse listener thread.
        updater (Thread): Thread used to update hold time for each step in the
                          list widget.
    """
    def __init__(self, listWidget, totalTimeDisp):
        """Initializes instance variables, and connects and starts listeners.

        Args:
            listWidget (KeyListWidget): The sole list widget displayed in the
                                        program.
            totalTimeDisp (QLCDNumber): Widget to display total time this macro
                                        takes.
        """
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

        self.keyboard = keyboard.Listener(on_press=self.onPressEmit, 
                on_release=self.onReleaseEmit)
        self.mouse = mouse.Listener(on_click=self.onClickEmit,
                on_scroll=self.onScrollEmit)

        self.keyboard.start()
        self.mouse.start()

    @synchronize
    def _clearRecordState(self):
        """Synchonously clears the keysDown dict."""
        self.keysDown.clear()

    def _runMacro(self, steps, time, loopNum, keys, recorder):
        """Runs a macro represented by the passed in data.

        Args:
            steps (List): List of tuples containing the data of each step.
                          More details in KeyListWidgetStep.
            time (float): Time it takes to run this macro.
            loopNum (int): Number of times to run this macro.
            keys (set): Set of KeyCodes which make up the hotkey that maps
                        to this macro.
            recorder (Hotkeys): Hotkey recorder used throughout the program.

        """
        runner = MacroRunner(steps, time, loopNum, self.mouseController, 
                self.keyController, keys, recorder)
        runner.start()

    def setRecordTotalTime(self, time):
        self.recordTotalTime = time

    def onBack(self):
        # only reset recordTotalTime if no longer on same macro, need to reload
        # this when changing macros
        self.setRecordTotalTime(0)

    def toggleRecord(self, record):
        """Toggles the recording state.

        If we begin recording, also start the updater thread.

        Args:
            record (bool): Whether or not to start recording.
        """
        if record:
            self.scrollEvent.reset(0)

            # Connect the list widget signals to update the widget on
            # the appropriate events.
            self.listWidget.keyPress.connect(self.keyboardEvent.onPress)
            self.listWidget.keyRelease.connect(self.keyboardEvent.onRelease)
            self.listWidget.mousePress.connect(self.clickEvent.onClick)
            self.listWidget.wait.connect(self.waitEvent.onWait)
            self.listWidget.mouseScroll.connect(self.scrollEvent.onScroll)

            # Stop listening for hotkeys while recording.
            self.listWidget.getCurrFocus().getRecorder().backupHotkeys()

            # update relavent instance variables
            self.recordStartTime = time.time()
            self.recording = True
            self.updater = Thread()
            self.startUpdater()
        else:

            # Disconnect functions from list widget signals
            # so we no longer add steps on each event.
            self.listWidget.keyPress.disconnect()
            self.listWidget.keyRelease.disconnect()
            self.listWidget.mousePress.disconnect()
            self.listWidget.wait.disconnect()
            self.listWidget.mouseScroll.disconnect()

            currFocus = self.listWidget.getCurrFocus()
            recorder = currFocus.getRecorder()

            # Put hotkeys back so user can use them again.
            recorder.reloadHotkeys()

            # Remove the last step because the last step was the click /
            # shortcut to stop recording which, when clicked / pressed again,
            # would begin recording again.
            self.listWidget.removeLast()

            # Stop updater (probably could've just self.updater.stop())
            self.recording = False
            self._clearRecordState()
            newTotalTime = time.time() - self.recordStartTime

            # If recordTotalTime is 0, then we can just set the total time
            # to the recently recorded total time, otherwise, we are recording
            # on an already existing macro, so we add the previous total time
            # to the recently recorded total.
            self.recordTotalTime = (newTotalTime if self.recordTotalTime == 0 
                    else self.recordTotalTime + newTotalTime)

            self.listWidget.parseSteps()
            self.listWidget.updateMacroList(self.recordTotalTime)

            hotkey = currFocus.getKeys()

            # Check if hotkey exists by checking if a mapping with the
            # same keys as the current macro exists. If so,
            # overrite that hotkey so we don't have any conflicting
            # macros. Otherwise, just add a new hotkey. 
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

    def canonize(func):
        """Decorator to remove modifier state from key events.
        
        Example: If we pressed ctrl+c, we would the c that would be passed into
                 the function would normally be some hex value \x03. Canonizing
                 the key would convert this value to 'c' before being bassed in.
        """
        return lambda self, key: func(self, self.keyboard.canonical(key))

    @canonize
    def onPressEmit(self, key):
        """Emits signal to listWidget to update with key press step.
        
        Args:
            key (KeyCode): Key pressed.
        """
        self.listWidget.keyPress.emit(self.startTime, key)

    @canonize
    def onReleaseEmit(self, key):
        """Emits signal to listWidget to update with key released.
        
        Args:
            key (KeyCode): Key released.
        """
        self.listWidget.keyRelease.emit(self.startTime, key)

    def onClickEmit(self, x, y, button, pressed):
        """Emits signal to listWidget to update with a mouse click.

        Args:
            x (int): X coordinate of mouse press.
            y (int): Y coordinate of mouse press.
            button (Enum (I think?)): Left or right click.
            pressed (bool): Whether the mouse was clicked or not.
        """
        self.listWidget.mousePress.emit(self.startTime, x, y, button, pressed)

    def onWaitEmit(self):
        """Emits signal to listWidget to update when user does nothing."""
        self.listWidget.wait.emit(self.startTime)

    def onScrollEmit(self, x, y, dx, dy):
        """Emite signal to listWidget to update with scroll step.

        Args:
            x (int): Current x position of the scroll wheel.
            y (int): Current y position of the scroll wheel.
            dx (int): X offset from last scroll wheel position.
            dy (int): Y offset from last scroll wheel position.
        """
        self.listWidget.mouseScroll.emit(self.startTime, x, y, dx, dy)

    def startUpdater(self):
        """Begins the thread that updates the hold time for each step."""
        if not self.updater.is_alive():
            self.updater = Thread(target=self._update)
            self.updater.start()

    @synchronize
    def _updateTime(self):
        """Updates the hold time for each step in the holdKeys dict."""
        for key, timeTup in self.keysDown.items():
            # Mouse scrolls have their own means of doing this
            if not key == StepEnum.MOUSE_SCROLL:
                timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))

    def _update(self):
        """Updates the hold time for each event in the holdKeys dict.
        
        This is the function that's run by the thread.
            
        """
        while self.recording:
            self.startTime = time.time() - self.recordStartTime + \
                    self.recordTotalTime
            if StepEnum.MOUSE_SCROLL in self.keysDown:
                self.scrollEvent.update()
            self.onWaitEmit()
            self._updateTime()

            # sleep to save cpu cycles
            time.sleep(.1)

    def shutdown(self):
        PostQuitMessage(0)
        # stop relavent threads?

