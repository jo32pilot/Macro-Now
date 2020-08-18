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

    def recordHotkey(self, original=None, steps=None, totalTime=0,
            updater=lambda: None):
        # TODO add param keys, if keys not none, then there was already a hotkey
        # for macro, so we replace instead of adding a new one
        # TODO if no steps and total time passed in, add default function
        # for hot key (attach different event to listener)
        self.currSteps = steps
        self.currTotalTime = totalTime
        self.savedHotkeys = self.mapper._hotkeys
        print(f'saved: {self.savedHotkeys} mapper: {self.mapper._hotkeys}')
        self.mapper._hotkeys = []
        self.updater = updater
        if not self.hotkeyRecorder or not self.hotkeyRecorder.is_alive():
            onRelease = lambda key: self.onReleaseRecordHotkey(original)
            self.hotkeyRecorder = keyboard.Listener(
                    on_press=self.onPressRecordHotkey, 
                    on_release=onRelease)
            self.hotkeyRecorder.start()

    def onPressRecordHotkey(self, key):
        self.currRecordSet.add(key)
        for mapping in self.savedHotkeys:
            conflicting = self.currRecordSet.issubset(mapping._keys) \
                    or mapping._keys.issubset(self.currRecordSet)
            if conflicting:
                # TODO make both red / warn user
                print(f'keys: {mapping._keys} curr {self.currRecordSet}')
                print('conflicting hotkeys')

    def _finishRecording(self):
        self.currRecordSet = set()
        self.currSteps = None
        self.currTotalTime = None
        self.hotkeyRecorder.stop()
        self.mapper._hotkeys = self.savedHotkeys + self.mapper._hotkeys
        self.updater = lambda: None

    # TODO combine bottom three
    def onReleaseRecordHotkey(self, original=None):
        # TODO need to stop editing
        if original:
            idx = self.findHotkey(original)
            if idx == -1: 
                # This case should never happen
                print(f'{original} doesn\'t exist even though it should')
            else:
                self.setHotkey(idx, self.currRecordSet, self.currSteps,
                        self.currTotalTime)
            
        else:
            self.addHotkey(self.currRecordSet, self.currSteps,
                    self.currTotalTime)
        self.updater(self.currRecordSet)
        self._finishRecording()

    # on user begin edit key sequence
    # set mappper hot keys to empty temporarily
    #
    # don't need to replace listener, just create a new one and stop it when 
    # needed
    #
    # on key press
    # if key sequence set found is subset of another set in mapper
    #   highlight red with existing map even if one contains more keys than the
    #   other
    #
    # on key release
    # stop editing, add hotkey (behavior undefined if red)
    #
    # need to make own display

    def addHotkey(self, keys, steps=None, totalTime=0, recording=True):
        # each macro widget will have the step data to pass in and total time
        # may need more parsing logic for hotkey
        addTo = self.savedHotkeys if recording else self.mapper._hotkeys
        func = (lambda: self.keyWatcher._runMacro(steps, totalTime)) \
                if steps and totalTime else (lambda: print(f'{keys} added'))
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
        keys = keys
        for idx, mapping in enumerate(findIn):
            if keys == set(mapping._keys):
                return idx
        return -1

    def setHotkey(self, idx, keys, steps=None, totalTime=0, recording=True):
        addTo = self.savedHotkeys if recording else self.mapper._hotkeys
        func = (lambda: self._runMacro(steps, totalTime)) \
                if steps and totalTime else (lambda: print(f'{keys} set'))
        hotkey = HotKey(keys, lambda: self.keyWatcher._runMacro(steps, totalTime))
        addTo[idx] = hotkey


