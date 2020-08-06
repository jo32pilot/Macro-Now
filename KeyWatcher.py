from pyHook import HookManager
from pyHook import HookConstants
from win32gui import PostQuitMessage
from PyQt5.QtWidgets import QListWidgetItem
from StepConstants import StepEnum

class KeyWatcher():

    def __init__(self, window, currentTime, diffTime, totalTime):
        self.currentTime = currentTime
        self.diffTime = diffTime
        self.totalTime = totalTime

        self.hm = HookManager()
        self.hm.HookKeyboard()
        self.hm.HookMouse()

        self.hm.SubscribeKeyAll(self.on_keyboard_event)
        #self.hm.SubscribeMouseAll()

        self.window = window

    def on_key_up_event(self, event):
        print(event.KeyID)
        return True

    def on_keyboard_event(self, event):
        if self.window.recordButton.isChecked():
            #self.window.listWidget.addItem(QListWidgetItem(chr(event.KeyID)))
            self.window.listWidgetAddStep(StepEnum.ACTIVE_WAIT)
            self.window.listWidgetAddStep(StepEnum.MOUSE_LEFT, (1, 2))
            self.window.listWidgetAddStep(StepEnum.KEY)
        return True            

    def your_method(self):
        self.new_wind = SubWindow()
        self.new_wind.show()

    def shutdown(self):
        PostQuitMessage(0)
        self.hm.UnhookKeyboard()

    def start_record_event(self):
        pass
