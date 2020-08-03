from pyHook import HookManager
from pyHook import HookConstants
from win32gui import PostQuitMessage

class KeyWatcher(object):

    def __init__(self, window, currentTime, diffTime, totalTime):
        self.currentTime = currentTime
        self.diffTime = diffTime
        self.totalTime = totalTime

        self.hm = HookManager()
        self.hm.HookKeyboard()
        self.hm.HookMouse()

        #self.hm.SubscribeKeyAll()
        #self.hm.SubscribeMouseAll()

        self.window = window

    def on_key_up_event(self, event):
        print(event.KeyID)
        return True

    def on_keyboard_event(self, event):
        print(event.KeyID)
        try:
            if event.KeyID  == ord('E'):
                self.your_method()
        finally:
            return True

    def your_method(self):
        self.new_wind = SubWindow()
        self.new_wind.show()

    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()
