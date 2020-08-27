"""File containing all step events.

Each StepEvent is a callback called when the respective signal is emitted.
The StepEvent will update what the list widget displays.
Event state is also kept by a shared dictionary (initialized in KeyWatcher).
"""

from util import synchronize, parseKey
from StepConstants import StepEnum
from pynput import mouse
import time

class StepEvent():
    """Base class for all step events.

    Attributes:
        listWidget (QListWidget): List widget to update.
        keysDown (dict): Mapping of keys currently pressed
                         (or if scrolling / clicking) to a tuple containing
                         their time held display and the time they were 
                         detected.
        lock (Lock): Threading lock to prevent race conditions in the keysDown
                     dict which can happen between the display updater thread
                     and the listener threads.
    """
    def __init__(self, listWidget, keysDown, lock):
        """Initializes instance variables.

        Args:
            listWidget (QListWidget): List widget to emit signals to.
            keysDown (dict): Mapping of keys currently pressed
                             (or if scrolling / clicking) to a tuple containing
                             their time held display and the time they were 
                             detected.
            lock (Lock): Threading lock to prevent race conditions in the
                         keysDown dict which can happen between the display
                         updater thread and the listener threads.

        """
        self.listWidget = listWidget
        self.keysDown = keysDown
        self.lock = lock

    @synchronize
    def _dictAdd(self, key, val):
        """Synchronously adds a key value pair to the keys down dictionary.

        Args:
            key (Object): Key to to hash.
            val (Object): Value the key maps to.
        """
        self.keysDown[key] = val

    @synchronize
    def _dictDel(self, key):
        """Synchonously deletes a key value pair from the keys down dictionary.

        Args:
            key (Object): Key whose corresponding key value pair will be deleted
                          from the dictionary.
        """
        timeTup = self.keysDown.get(key, None)
        if timeTup != None:
            del self.keysDown[key]


class KeyboardEvent(StepEvent):
    """Event class for keyboard events."""

    def onPress(self, startTime, key):
        """Callback for when a key is pressed.

        This adds a new step to the list widget as well as updating the
        state dictionary with key pressed.

        Args:
            startTime (float): When this step started relative to the start
                               of the macro.
            key (KeyCode): Key pressed.
        """
        if key not in self.keysDown:
            key = str(key)
            press = self.listWidget.listWidgetAddStep(
                    startTime, StepEnum.KEY, parseKey(key)).getPress()
            self._dictAdd(key, (press, time.time()))

    def onRelease(self, startTime, key):
        """Callback for when a key is released.

        Just deletes the key from the state dictionary.

        Args:
            startTime (float): When this step started relative to the start
                               of the macro. (Actually probably don't need this 
                               for this callback).
            key (KeyCode): Key pressed.
        """
        self._dictDel(key)

class ClickEvent(StepEvent):
    """Event class for click events.

    Attributes:
        dataCache (dict): Mapping of type of click -> data of the click. The
                          data is a tuple containing the widget that displays
                          the data, and the coordinates of the initial click.
                          This is used to determine if the the event is actually
                          a drag event and to update the widget accordingly if
                          it is a drag event.
    """
    def __init__(self, listWidget, keysDown, lock):
        """Initializes instnace variables.

        Args:
            listWidget (QListWidget): See StepEvent.
            keysDown (dict): See StepEvent.
            lock (Lock): See StepEvent.
        """
        super().__init__(listWidget, keysDown, lock)
        self.dataCache = {StepEnum.MOUSE_LEFT: None, StepEnum.MOUSE_RIGHT: None}

    def onClick(self, startTime, x, y, button, pressed):
        """Callback for when a key is pressed.

        This function adds the appropriate step enum into the state dictionary.
        It adds to the dataCache dictionary.

        Args:
            startTime (float): When this step started relative to the start
                               of the macro.
            x (int): X coordinate of the click.
            y (int): Y coordinate of the click.
            button (Enum (I think?)): Which mouse button clicked.
            pressed (bool): Whether the mouse was clicked or released.
        """
        stepType = StepEnum.MOUSE_LEFT if button == mouse.Button.left else \
                StepEnum.MOUSE_RIGHT
        if pressed:
            container = self.listWidget.listWidgetAddStep(
                    startTime, stepType, (x, y))
            press = container.getPress()
            self._dictAdd(button, (press, time.time()))
            self.dataCache[stepType] = (container, x, y)
        else:
            self._dictDel(button)
            # If user dragged mouse, update container
            container, oldX, oldY = self.dataCache[stepType]
            if oldX != x or oldY != y:
                container.clickToDrag(stepType, (oldX, oldY), (x, y))

class WaitEvent(StepEvent):
    """Event class for when the user isn't doing anything."""

    def onWait(self, startTime):
        """Callback for when the user isn't doing anything.

        Args:
            startTime (float): When this step started relative to the start
                               of the macro.
        """

        # If the event state dictionary is empty, then the user isn't doing
        # anything.
        if len(self.keysDown) == 0:
            press = self.listWidget.listWidgetAddStep(
                    startTime, StepEnum.ACTIVE_WAIT, None).getPress()
            self._dictAdd(StepEnum.ACTIVE_WAIT, (press, time.time()))
        elif StepEnum.ACTIVE_WAIT in self.keysDown and len(self.keysDown) > 1:
            self._dictDel(StepEnum.ACTIVE_WAIT)

class ReleaselessEvent(StepEvent):
    """Event parent class for events that can't detect if the event is finished.

    This class is used for events like scroll events and move events
    (move event is no longer implemented). Events like these don't 
    have a means to signal that they are done. When we add steps like thesei to
    the list widget, we don't want to add each individual scroll tick
    or coordinate change. Instead, we condense the event into one step
    and when the event doesn't occur for some time offset, we 
    say that event is finished.

    Attributes:
        data (Tuple | float): Step data for this event.
        stopStart (float): When the user stopped performing the event.
        stopDelta (float): Time since the user stopped performing the event.
        endPosWidget (QWidget): Widget to display the step's data.
        check (bool): Whether or not the event occured since the last update.
    """

    def __init__(self, data, listWidget, keysDown, lock):
        """Initializes base class and 0 initializes instance variables.

        Args:
            data (Tuple | float): Step data for this event.
            listWidget (QListWidget): See StepEvent.
            keysDown (dict): See StepEvent.
            lock (Lock): See StepEvent.
        """
        super().__init__(listWidget, keysDown, lock)
        self.reset(data)

    def reset(self, data):
        """Resets instance variables.

        Args:
            data (Tuple | float): Step data for this event to set to the data
                                  member.

        """
        self.data = data
        self.stopStart = 0
        self.stopDelta = 0
        self.endPosWidget = None
        self.check = False

    def _onEvent(self, startTime, stepType, data, increment=False):
        """Callback for when this event occurs.

        Args:
            startTime (float): When this step started relative to the start
                               of the macro.
            stepType (StepEnum): Type of this step.
            data (Tuple | float): Step data for this event.
            incremement (bool): Whether or not to add the passed in data
                                to the data member or to set the passed in
                                data as the data member.

        """

        # If the event isn't already in the event state dictionary.
        if stepType not in self.keysDown:
            defaultData = self.data if increment else [self.data, data]
            container = self.listWidget.listWidgetAddStep(
                    startTime, stepType, defaultData)

            press = container.getPress()
            self.endPosWidget = container.getEditable()
            self.stopStart = time.time()

            self._dictAdd(stepType, (press, time.time()))
        # Otherwise, update the current event data.
        else:
            if increment:
                self.data += data
            else:
                self.data = data

            # The event occurred just now, so reset stopStart.
            self.stopStart = time.time()
        self.check = True

    def _update(self, stepType, updateFunc, reset=False):
        """Updates data and hold time displayed in this step's widget.

        Args:
            stepType (StepEnum): Type of this step.
            updateFunc (func): Function to call to update displayed step data.
            reset (bool): If we want to reset the data to 0 upon finishing the
                          event. If mouse events were still implemented, this
                          would matter more because we would want the initial 
                          data for the next mouse move event to be where the 
                          last move event stopped.

        """
        # If the event hasn't occured for 1 second.
        # TODO make configurable
        if self.stopDelta >= 1 and self.endPosWidget != None:
            self.stopDelta = 0
            if reset:
                self.data = 0
            self._dictDel(stepType)
            self.endPosWidget = None
        # Otherwise if the event hasn't occured for less than the
        # threshold, update the time passed since the event last
        # occured.
        elif not self.check:
            self.stopDelta = time.time() - self.stopStart
        # Otherwise the event recently occured, so update the correct
        # members and display.
        elif self.check:
            updateFunc()
            timeTup = self.keysDown[stepType]
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            self.check = False

# Why not merge ReleaselessEvent into scroll event and avoid needless
# inheritance? Because there previously was a mouse move event which also needed
# the functionality of ReleaselessEvent. It was removed in favor of mouse click
# drags but may be reimplemented in the future.
class ScrollEvent(ReleaselessEvent):
    """Event class for scroll events."""

    def onScroll(self, startTime, x, y, dx, dy):
        """Callback for when the mouse is scrolled.
        
        Args:
            startTime (float): When this step started relative to the start
                               of the macro.
            x (int): Current x position of the scroll wheel.
            y (int): Current y position of the scroll wheel.
            dx (int): X offset from last scroll wheel position.
            dy (int): Y offset from last scroll wheel position.
        """
        self._onEvent(startTime, StepEnum.MOUSE_SCROLL, dy, increment=True)

    def _updateText(self):
        """Updates the data display in this step's widget."""
        self.endPosWidget.setText(str(self.data))

    def update(self):
        """Updates the widget's data display and hold time.
        
        This method is what's called in the updater thread of KeyWatcher.
        """
        self._update(StepEnum.MOUSE_SCROLL, self._updateText, reset=True)

