
class Hotkeys():
    def __init__(self):
        self.savedHotKeys = None
        self.mapper = keyboard.GlobalHotKeys({})
        self.hotkeyRecorder = mouse.Listener() #TODO

        self.mapper.start()

    def recordHotkey(self):
        self.savedHotkeys = self.mapper._hotkeys
        self.mapper._hotkeys = []
        if not self.hotkeyRecorder.is_alive():
            self.hotkeyRecorder = mouse.Listener() # TODO
            self.hotkeyRecorder.start()

    def onPressRecordHotkey(self, key):
        

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

    def addHotkey(self, keys, steps, totalTime):
        # each macro widget will have the step data to pass in and total time
        # may need more parsing logic for hotkey
        hotkey = HotKey(HotKey.parse(keys),
                lambda: self._runMacro(steps, totalTime))
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

    def setHoykey(self, idx, steps, totalTime):
        hotkey = HotKey(HotKey.parse(keys),
                lambda: self._runMacro(original, steps, totalTime))
        self.mapper._hotkeys[idx] = hotkey

