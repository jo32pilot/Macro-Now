"""File containing the hotkey recording logic."""

from DoubleClickWidgets import EditLabelKeySequence
from pynput import keyboard
from pynput.keyboard import HotKey

class Hotkeys():
    """This class wraps pynput's GlobalHotKeys to record and store hotkeys.
    
    Recording is done via another instance of pynput's keyboard listener thread.

    Attributes:
        savedHotkeys (list): List of HotKey objects. This is used to save the
                             hotkeys mapped in GlobalHotKeys before emptying
                             this mapping. We do generally do this when we
                             don't want a hotkey's event to go off like
                             when recording a new macro or when a macro is
                             running.
        currRecordSet (set): Set used to keep track of keys pressed during 
                             the recording of a new hotkey.
        currSteps (list): List of macro steps to map to the currently recording
                          hotkey.
        currTotalTime (float): Total time to run the macro that will be mapped
                               to the currently recording hotkey.
        keyWatcher (KeyWatcher): Macro recorder that's used throughout the
                                 program.
        mapper (GlobalHotKeys): Pynput's GlobalHotKeys object to listen for 
                                the recorded hotkeys and play their respective
                                events.
        updater (func): Function to call after the hotkey is finished recording.
                        This is generally used to update the GUI.
    """

    def __init__(self, keyWatcher):
        """Initializes instance variables and starts the GlobalHotKey thread.
        
        Args:
            keyWatcher (KeyWatcher): Macro recorder that's used throughout the
                                     program.
        """
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
        """Backs up and clears the hotkeys in the hotkey listener."""
        self.savedHotkeys = self.mapper._hotkeys
        self.mapper._hotkeys = []

    def reloadHotkeys(self):
        """Reloads saved hot keys into the hotkey listener.
        
        This function assumes that backupHotkeys was called before it.
        """

        # When pressing a hotkey to run a macro, the macro begins to run
        # before the state of the hotkey (which keys are pressed) is updated.
        # So the keys pressed to run the macro are still in the state, meaning
        # we have to press the hotkey twice to run the macro again (once to 
        # remove the keys from the state, another to run the macro again).
        # To prevent this, we manually reset the state of each hotkey.
        for hotkey in self.savedHotkeys:
            hotkey._state = set()

        self.mapper._hotkeys = self.savedHotkeys
        self.savedHotkeys = None

    def recordHotkey(self, original=None, steps=None, totalTime=0, loopNum=0,
            updater=lambda param: None, customFunc=lambda: None):
        """Begins recording a hotkey.

        This function mainly sets up the state of the object while recording
        so that after the recording is finished, the correct functionaliy will
        be mapped to the hotkey. It also starts the keyboard listener thread.

        Args:
            original (set): If we recording to overwrite an existing mapping,
                            this is the set of KeyCodes that made up the
                            original mapping and which will be subsequently
                            replaced by the newly recorded hotkey.
            steps (list): List of macro steps to map to the currently recording
                          hotkey.
            totalTime (float): Total time to run the macro that will be
                                   mapped to the currently recording hotkey.
            loopNum (int): Number of times to loop the macro.
            updater (func): Function to call after the hotkey is finished
                            recording. This is generally used to update the GUI.
            customFunc (func): Function to map to the hotkey if this hotkey
                               is not being used for a macro.
        """

        # Set up object state for when we finish recording the hotkey
        self.currSteps = steps
        self.currTotalTime = totalTime
        self.savedHotkeys = self.mapper._hotkeys
        self.loopNum = loopNum
        self.mapper._hotkeys = []
        self.updater = updater

        # Starts the keyboard listener thread
        if not self.hotkeyRecorder or not self.hotkeyRecorder.is_alive():
            onRelease = lambda key: self.onReleaseRecordHotkey(original,
                    customFunc)
            self.hotkeyRecorder = keyboard.Listener(
                    on_press=self.onPressRecordHotkey, 
                    on_release=onRelease)
            self.hotkeyRecorder.start()

    def onPressRecordHotkey(self, key):
        """Function ran when key is pressed when recording a new hotkey.

        A new key is added to the hotkey and we check if this new hotkey
        or a subset of the keys pressed already exists.
        
        Args:
            key (KeyCode): Key pressed
        """

        # See KeyWatcher for what canonical does
        key = self.hotkeyRecorder.canonical(key)
        self.currRecordSet.add(key)

        # Check every hotkey if it's keys is a nonproper subset of
        # the current hotkey or if the current hotkey's keys is a nonproper
        # subset of any other hotkey.
        for mapping in self.savedHotkeys:
            conflicting = self.currRecordSet.issubset(mapping._keys) \
                    or mapping._keys.issubset(self.currRecordSet)
            if conflicting:
                # TODO make both red / warn user
                print(f'keys: {mapping._keys} curr {self.currRecordSet}')
                print('conflicting hotkeys')

    def finishRecording(self):
        """Clean up state of object after recording is finished."""
        self.currRecordSet = set()
        self.currSteps = None
        self.currTotalTime = None
        self.hotkeyRecorder.stop()

        # I don't remember why this line is a thing but I'm sure it's for a
        # good reason. Will re-comment if I rememberi
        self.mapper._hotkeys = self.savedHotkeys + self.mapper._hotkeys

        self.updater = lambda: None
        EditLabelKeySequence.recording = False

    def onReleaseRecordHotkey(self, original=None, customFunc=lambda: None):
        """Function ran when key is released when recording a new hotkey.

        Whenever any of the held keys is released, we stop recording.

        If we find a hotkey with keys identical to the original keys,
        then we replace the existing hotkey mapping with the new one. This could
        mean that if multiple mappings had the same keys, then we could end up
        replacing a different mapping. This should be taken care of in future 
        updates. Otherwise, if not such hotkey exists, we just add a new one.

        Args:
            original (set): Set of keys that we check if a hotkey with
                            an identical set already exists.
            customFunc (func): Function to map to the hotkey if this hotkey
                               is not being used for a macro.
        """
        if original:
            idx = self.findHotkey(original)

            # -1 denotes that no such identical hotkey was found
            if idx != -1:
                self.setHotkey(idx, self.currRecordSet, self.currSteps,
                        self.currTotalTime, self.loopNum, customFunc)
            else:
                self.addHotkey(self.currRecordSet, self.currSteps,
                        self.currTotalTime, self.loopNum, customFunc)
        else:
            self.addHotkey(self.currRecordSet, self.currSteps,
                    self.currTotalTime, self.loopNum, customFunc)

        # The updater was only needed for EditLabelKeySequence to update
        # state and GUI so this feels a little hacky / not generic.
        self.updater(self.currRecordSet)

        self.finishRecording()

    def addHotkey(self, keys, steps=None, totalTime=0, loopNum=0,
            customFunc=lambda: None, recording=True):
        """Adds a new hotkey mapping to savedHotKeys or the mapper object.

        Args:
            keys (set): Set of KeyCodes that will map to some functionality.
            steps (list): List of macro steps to map to the hotkey.
            totalTime (float): Total time to run the macro that will be
                                   mapped to the hotkey.
            loopNum (int): Number of times to loop the macro.
            customFunc (func): Function to map to the hotkey if this hotkey
                               is not being used for a macro.
            recording (bool): Whether or not we're calling this function
                              because we've recorded a new hotkey. This
                              denotes if the hotkey will be added to either
                              savedHotKeys (if recording is True) or if the 
                              hotkey will be added to the mapper itself
                              (if recording is False). This is needed because
                              sometimes we would like to add a new hotkey
                              aside from when we've just recorded a new one.
                              For example, we would like to add hotkeys
                              to the mapper when we start up the application
                              and have read the saved hotkeys from disc.

        """
        addTo = self.savedHotkeys if recording else self.mapper._hotkeys
        # If steps, totalTime, and loopNum weren't passed in / are inherintly
        # False, then that means this hotkey will not be used for a macro,
        # so we mapm the custom function instead.
        func = lambda: self.keyWatcher._runMacro(steps, totalTime, loopNum,
                keys, self) if steps and totalTime and loopNum else customFunc
        hotkey = HotKey(keys, func)
        addTo.append(hotkey)

    def findHotkey(self, keys, recording=True):
        """Searches for existing hotkey in either savedHotkeys or the mapper.

        Args:
            keys (set): List of KeyCodes to find in the correct list.
            recording (bool): Whether or not we're calling this function
                              because we've recorded a new hotkey. This
                              denotes if the hotkey will be searched for in
                              either savedHotKeys (if recording is True) or if
                              the hotkey will be searched for in the mapper
                              itself (if recording is False). This is needed
                              because sometimes we would like to search for a
                              hotkey aside from when we've just recorded a new
                              one. For example, we've changed the number of
                              times the macro will loop for, and want to find
                              the HotKey the macro maps to so we can replace
                              it with a HotKey that loops the macro the 
                              correct number of times.

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
        """Replace the hotkey at idx in either savedHotkeys or the mapper.

        Args:
            idx (int) Index of the hotkey to replace.
            keys (set): Set of KeyCodes that will map to some functionality.
            steps (list): List of macro steps to map to the hotkey.
            totalTime (float): Total time to run the macro that will be
                                   mapped to the hotkey.
            loopNum (int): Number of times to loop the macro.
            customFunc (func): Function to map to the hotkey if this hotkey
                               is not being used for a macro.
            recording (bool): Whether or not we're calling this function
                              because we've recorded a new hotkey. This
                              denotes if the hotkey will replace an existing 
                              hotkey in either savedHotKeys (if recording is
                              True) or the mapper itself (if recording is
                              False). This is needed because sometimes we would
                              like to replace a hotkey aside from when we've
                              just recorded a new one. For example, we've
                              changed the number of times the macro will loop
                              for, and want to replace it with a HotKey that
                              loops the macro the correct number of times.
        """
        if idx < 0:
            print('Tried to set at -1 -> hotkey doesn\'t exist')
            return
        addTo = self.savedHotkeys if recording else self.mapper._hotkeys
        # If steps, totalTime, and loopNum weren't passed in / are inherintly
        # False, then that means this hotkey will not be used for a macro,
        # so we map the custom function instead.
        func = lambda: self.keyWatcher._runMacro(steps, totalTime, loopNum,
                keys, self) if steps and totalTime and loopNum else customFunc
        hotkey = HotKey(keys, func)
        addTo[idx] = hotkey

    def setMacroToggle(self, keys, toggleFunc):
        """Used to stop a macro if the macro was set to loop until hotkey press.

        Args:
            keys (set): Set of KeyCodes the macro maps to which will stop the
                        looping.
            toggleFunc (func): Function to run which will stop running the
                               macro.

        """
        hotkey = HotKey(keys, toggleFunc)
        self.mapper._hotkeys.append(hotkey)

