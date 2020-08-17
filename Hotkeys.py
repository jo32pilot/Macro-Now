from pynput import keyboard

class Hotkeys():
    def __init__(self, keyWatcher):
        self.savedHotKeys = None
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
        curr.currTotalTime = totalTime
        self.savedHotkeys = self.mapper._hotkeys
        self.mapper._hotkeys = []
        self.updater = updater
        if not self.hotkeyRecorder or not self.hotkeyRecorder.is_alive():
            self.hotkeyRecorder = keyboard.Listener(
                    on_press=self.onPressRecordHotKey, 
                    on_release=self.onReleaseRecordHotKey)
            self.hotkeyRecorder.start()

    def onPressRecordHotkey(self, key):
        self.currRecordSet.add(key)
        hotkey = set(HotKey.parse(self.currRecordSet))
        for mapping in self.savedHotKeys:
            conflicting = self.currRecordSet.issubset(mapping._keys) \
                    or mapping._keys.issubset(self.currRecordSet)
            if conflicting:
                # TODO make both red / warn user
                print('conflicting hotkeys')

    def _finishRecording(self):
        self.selfRecordSet = set()
        self.currSteps = None
        self.currTotalTime = None
        self.hotkeyRecorder.stop()
        self.mapper._hotkeys = self.savedHotKeys
        self.updater = lambda: None

    # TODO combine bottom three
    def onReleaseRecordHotKey(self, original=None):
        # TODO need to stop editing
        if original:
            idx = self.findHotKey(original)
            if idx == -1: 
                # This case should never happen
                print(f'{keys} doesn\'t exist even though it should')
            else:
                self.setHotKey(idx, self.currRecordSet, self.currSteps,
                        self.currTotalSet)
            
        else:
            self.addHotKey(self.currRecordSet, self.currSteps,
                    self.currTotalTime)
        self.updater()
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

    def addHotkey(self, keys, steps=None, totalTime=0):
        # each macro widget will have the step data to pass in and total time
        # may need more parsing logic for hotkey
        func = (lambda: self._runMacro(steps, totalTime)) \
                if steps and totalTime else (lambda: print(f'{keys} added'))
        hotkey = HotKey(HotKey.parse(keys), func)
        self.mapper._hotkeys.append(hotkey)

    def findHotkey(self, keys):
        """Searches for existing hotkey in mapper.

        Args:
            keys (string): List of keys in string representation. These
                    keys make up the hotkey.

        Returns:
            int: Index of hotkey in mapper if found. -1 if not found.


        """
        keys = HotKey.parse(keys)
        for idx, mapping in enumerate(self.mapper._hotkeys):
            if keys == set(mapping._keys):
                return idx
        return -1

    def setHotkey(self, idx, keys, steps=None, totalTime=0):
        func = (lambda: self._runMacro(steps, totalTime)) \
                if steps and totalTime else (lambda: print(f'{keys} set'))
        hotkey = HotKey(HotKey.parse(keys),
                lambda: self._runMacro(steps, totalTime))
        self.mapper._hotkeys[idx] = hotkey


