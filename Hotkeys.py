from DoubleClickWidgets import EditLabelKeySequence
from pynput import keyboard
from pynput.keyboard import HotKey

class Hotkeys():
    def __init__(self, keyWatcher):
        self.savedHotkeys = None
        self.currRecordSet = set()
        self.currSteps = None
        self.currTotalTime = 0
        self.keyWatcher = keyWatcher
        self.mapper = keyboard.GlobalHotKeys({})
        self.hotkeyRecorder = None
        self.updater = lambda: None

        self.mapper.start()

    def backupHotkeys(self):
        self.savedHotkeys = self.mapper._hotkeys
        self.mapper._hotkeys = []

    def reloadHotkeys(self):
        for hotkey in self.savedHotkeys:
            hotkey._state = set()
        self.mapper._hotkeys = self.savedHotkeys
        self.savedHotkeys = None

    def recordHotkey(self, original=None, steps=None, totalTime=0, loopNum=0,
            updater=lambda param: None, customFunc=lambda: None):
        # TODO add param keys, if keys not none, then there was already a hotkey
        # for macro, so we replace instead of adding a new one
        # TODO if no steps and total time passed in, add default function
        # for hot key (attach different event to listener)
        self.currSteps = steps
        self.currTotalTime = totalTime
        self.savedHotkeys = self.mapper._hotkeys
        self.loopNum = loopNum
        self.mapper._hotkeys = []
        self.updater = updater
        if not self.hotkeyRecorder or not self.hotkeyRecorder.is_alive():
            onRelease = lambda key: self.onReleaseRecordHotkey(original,
                    customFunc)
            self.hotkeyRecorder = keyboard.Listener(
                    on_press=self.onPressRecordHotkey, 
                    on_release=onRelease)
            self.hotkeyRecorder.start()

    def onPressRecordHotkey(self, key):
        key = self.hotkeyRecorder.canonical(key)
        self.currRecordSet.add(key)
        for mapping in self.savedHotkeys:
            conflicting = self.currRecordSet.issubset(mapping._keys) \
                    or mapping._keys.issubset(self.currRecordSet)
            if conflicting:
                # TODO make both red / warn user
                print(f'keys: {mapping._keys} curr {self.currRecordSet}')
                print('conflicting hotkeys')

    def finishRecording(self):
        self.currRecordSet = set()
        self.currSteps = None
        self.currTotalTime = None
        self.hotkeyRecorder.stop()
        self.mapper._hotkeys = self.savedHotkeys + self.mapper._hotkeys
        self.updater = lambda: None
        EditLabelKeySequence.recording = False

    def onReleaseRecordHotkey(self, original=None, func=lambda: None):
        if original:
            idx = self.findHotkey(original)
            if idx != -1:
                self.setHotkey(idx, self.currRecordSet, self.currSteps,
                        self.currTotalTime, self.loopNum, func)
            
        else:
            self.addHotkey(self.currRecordSet, self.currSteps,
                    self.currTotalTime, self.loopNum, func)
        self.updater(self.currRecordSet)
        self.finishRecording()

    def addHotkey(self, keys, steps=None, totalTime=0, loopNum=0,
            customFunc=lambda: None, recording=True):
        # each macro widget will have the step data to pass in and total time
        # may need more parsing logic for hotkey
        addTo = self.savedHotkeys if recording else self.mapper._hotkeys
        func = lambda: self.keyWatcher._runMacro(steps, totalTime, loopNum, keys, self) \
                if steps and totalTime and loopNum else customFunc
        hotkey = HotKey(keys, func)
        addTo.append(hotkey)

    def findHotkey(self, keys, recording=True):
        """Searches for existing hotkey in mapper.

        Args:
            keys (string): List of keys in string representation. These
                    keys make up the hotkey.

        Returns:
            int: Index of hotkey in mapper if found. -1 if not found.


        """
        findIn = self.savedHotkeys if recording else self.mapper._hotkeys
        for idx, mapping in enumerate(findIn):
            if keys == set(mapping._keys):
                return idx
        return -1

    def setHotkey(self, idx, keys, steps=None, totalTime=0, loopNum=0,
            customFunc=lambda: None, recording=True):
        if idx < 0:
            print('Tried to set at -1 -> hotkey doesn\'t exist')
            return
        addTo = self.savedHotkeys if recording else self.mapper._hotkeys
        func = lambda: self.keyWatcher._runMacro(steps, totalTime, loopNum, keys, self) \
                if steps and totalTime and loopNum else customFunc
        hotkey = HotKey(keys, func)
        addTo[idx] = hotkey

    def getHotkey(self, idx, recording=True):
        return self.savedHotkeys[idx] if recording \
                else self.mapper._hotkeys[idx]

    def addExistingHotkey(self, hotkey):
        self.mapper._hotkeys.append(hotkey)

    def setMacroToggle(self, keys, toggleFunc):
        hotkey = HotKey(keys, toggleFunc)
        self.mapper._hotkeys.append(hotkey)

