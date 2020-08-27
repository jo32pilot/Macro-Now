"""File for constants."""

import pynput._util.win32_vks as VK
from pynput.keyboard import Key, KeyCode
from enum import Enum

class StepEnum(Enum):
    """Enums for step types."""
    ACTIVE_WAIT = 0
    MOUSE_LEFT = 1
    MOUSE_RIGHT = 2
    MOUSE_SCROLL = 3
    MOUSE_LEFT_DRAG = 4
    MOUSE_RIGHT_DRAG = 5
    KEY = 6

    def __lt__(self, other):
        """Less than operator overload for enums.

        It doesn't actually matter which values are greater than which. We just
        need to override this because the priority queue in MacroRunner tie
        tie breaks by looking at StepEnum.

        Args:
            other (StepEnum): The other StepEnum to compare to.

        Return: True if the value of other is greater than self's value.
                False otherwise.
        """
        return self.value < other.value


_ENUM_CONST = {
    StepEnum.ACTIVE_WAIT: ('image: url(:/images/images/active_wait.png);\npadding:3px;', 'Active Wait Time'),
    StepEnum.MOUSE_LEFT: ('image: url(:/images/images/leftclick.png);\npadding:3px;', 'Mouse Left Click'),
    StepEnum.MOUSE_RIGHT: ('image: url(:/images/images/rightclick.png);\npadding:3px;', 'Mouse Right Click'),
    StepEnum.MOUSE_SCROLL: ('image: url(:/images/images/scroll.png);\npadding:3px;', 'Mouse Scroll'),
    StepEnum.MOUSE_LEFT_DRAG: ('image: url(:/images/images/left_drag.png);\npadding:3px;', 'Mouse Left Drag'),
    StepEnum.MOUSE_RIGHT_DRAG: ('image: url(:/images/images/right_drag.png);\npadding:3px;', 'Mouse Right Drag'),
    StepEnum.KEY: ('image: url(:/images/images/keyboard.png);\npadding:3px;', 'Key Press'),
}

_KEY_CONSTANTS = {
    'alt': Key.alt,
    'alt_gr': Key.alt_gr,
    'alt_l': Key.alt_l,
    'alt_r': Key.alt_r,
    'backspace': Key.backspace,
    'caps_lock': Key.caps_lock,
    'cmd': Key.cmd,
    'cmd_l': Key.cmd_l,
    'cmd_r': Key.cmd_r,
    'ctrl': Key.ctrl,
    'ctrl_l': Key.ctrl_l,
    'ctrl_r': Key.ctrl_r,
    'delete': Key.delete,
    'down': Key.down,
    'end': Key.end,
    'enter': Key.enter,
    'esc': Key.esc,
    'f1': Key.f1,
    'f2': Key.f2,
    'f3': Key.f3,
    'f4': Key.f4,
    'f5': Key.f5,
    'f6': Key.f6,
    'f7': Key.f7,
    'f8': Key.f8,
    'f9': Key.f9,
    'f10': Key.f10,
    'f11': Key.f11,
    'f12': Key.f12,
    'f13': Key.f13,
    'f14': Key.f14,
    'f15': Key.f15,
    'f16': Key.f16,
    'f17': Key.f17,
    'f18': Key.f18,
    'f19': Key.f19,
    'f20': Key.f20,
    'home':  Key.home,
    'insert': Key.insert,
    'left': Key.left,
    'media_next': Key.media_next,
    'media_play_pause': Key.media_play_pause,
    'media_previous': Key.media_previous,
    'media_volume_down': Key.media_volume_down,
    'media_volume_mute': Key.media_volume_mute,
    'media_volume_up': Key.media_volume_up,
    'menu': Key.menu,
    'num_lock': Key.num_lock,
    'page_down': Key.page_down,
    'page_up': Key.page_up,
    'pause': Key.pause,
    'print_screen': Key.print_screen,
    'right': Key.right,
    'scroll_lock': Key.scroll_lock,
    'shift': Key.shift,
    'shift_l': Key.shift_l,
    'shift_r': Key.shift_r,
    'space': Key.space,
    'tab': Key.tab,
    'up': Key.up,
}

_VK_CONST = {
    Key.alt : VK.MENU,
    Key.alt_l : VK.LMENU,
    Key.alt_r : VK.RMENU,
    Key.alt_gr : VK.RMENU,
    Key.backspace : VK.BACK,
    Key.caps_lock : VK.CAPITAL,
    Key.cmd : VK.LWIN,
    Key.cmd_l : VK.LWIN,
    Key.cmd_r : VK.RWIN,
    Key.ctrl : VK.CONTROL,
    Key.ctrl_l : VK.LCONTROL,
    Key.ctrl_r : VK.RCONTROL,
    Key.delete : VK.DELETE,
    Key.down : VK.DOWN,
    Key.end : VK.END,
    Key.enter : VK.RETURN,
    Key.esc : VK.ESCAPE,
    Key.f1 : VK.F1,
    Key.f2 : VK.F2,
    Key.f3 : VK.F3,
    Key.f4 : VK.F4,
    Key.f5 : VK.F5,
    Key.f6 : VK.F6,
    Key.f7 : VK.F7,
    Key.f8 : VK.F8,
    Key.f9 : VK.F9,
    Key.f10 : VK.F10,
    Key.f11 : VK.F11,
    Key.f12 : VK.F12,
    Key.f13 : VK.F13,
    Key.f14 : VK.F14,
    Key.f15 : VK.F15,
    Key.f16 : VK.F16,
    Key.f17 : VK.F17,
    Key.f18 : VK.F18,
    Key.f19 : VK.F19,
    Key.f20 : VK.F20,
    Key.home : VK.HOME,
    Key.left : VK.LEFT,
    Key.page_down : VK.NEXT,
    Key.page_up : VK.PRIOR,
    Key.right : VK.RIGHT,
    Key.shift : VK.LSHIFT,
    Key.shift_l : VK.LSHIFT,
    Key.shift_r : VK.RSHIFT,
    Key.space : VK.SPACE,
    Key.tab : VK.TAB,
    Key.up : VK.UP,
}

_VK_KEYS = {
    Key.up,
    Key.down,
    Key.left,
    Key.right,
}

def stepImage(step):
    return _ENUM_CONST[step][0]

def stepDescriptor(step):
    return _ENUM_CONST[step][1]

def keyConst(key):
    return _KEY_CONSTANTS[key]

def keyToVK(key):
    return _VK_CONST.get(key, key)

def isVKPress(key):
    return key in _VK_KEYS
