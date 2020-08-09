from win32gui import PostQuitMessage
from StepConstants import StepEnum
from pynput import mouse, keyboard
from threading import Thread, Lock
import time

# maybe can turn this all into snake case?

# what will happen to thread if not yet stopped and delete a step?


class KeyWatcher():

    def __init__(self, listWidget, currentTime, diffTime, totalTime):
        self.listWidget = listWidget
        self.currentTime = currentTime
        self.diffTime = diffTime
        self.totalTime = totalTime
        self.keysDown = dict()

        self.listWidget.keyPress.connect(self.onPress)
        self.listWidget.keyRelease.connect(self.onRelease)

        self.updater = Thread()
        self.lock = Lock()

        self.keyController = keyboard.Controller()

        self.keyboard = keyboard.Listener(on_press=self.onPressEmit, 
                on_release=self.onReleaseEmit)
        self.keyboard.start()

    def onPressEmit(self, key):
        self.listWidget.keyPress.emit(key)

    def onReleaseEmit(self, key):
        self.listWidget.keyRelease.emit(key)

    def onPress(self, key):

        if key not in self.keysDown:
            # when start recording, set self.currentTime to 0 and 
            # set start time
            press = self.listWidget.listWidgetAddStep(StepEnum.KEY, str(key))
            self.lock.acquire()
            self.keysDown[key] = (press, time.time())
            self.lock.release()
            if not self.updater.is_alive():
                self.updater = Thread(target=self.update)
                self.updater.start()

        '''
        for timeTup in self.keysDown.values():
            timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
        '''

        return True


    def onRelease(self, key):
        self.lock.acquire()
        del self.keysDown[key]
        self.lock.release()
        return True

    def update(self):
        while len(self.keysDown) != 0:
            self.lock.acquire()
            for timeTup in self.keysDown.values():
                timeTup[0].setText('%.2f' % (time.time() - timeTup[1]))
            self.lock.release()


    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()

    def start_record_event(self):
        pass
