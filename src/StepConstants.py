from pynput.keyboard import Key, KeyCode
from enum import Enum

class StepEnum(Enum):
    ACTIVE_WAIT = 0
    MOUSE_LEFT = 1
    MOUSE_RIGHT = 2
    MOUSE_SCROLL = 3
    MOUSE_LEFT_DRAG = 4
    MOUSE_RIGHT_DRAG = 5
    KEY = 6

    def __lt__(self, other):
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


def stepImage(step):
    return _ENUM_CONST[step][0]

def stepDescriptor(step):
    return _ENUM_CONST[step][1]

def keyConst(key):
    return _KEY_CONSTANTS[key]
