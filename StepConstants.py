from enum import Enum

class StepEnum(Enum):
    ACTIVE_WAIT = 0
    MOUSE_LEFT = 1
    MOUSE_RIGHT = 2
    MOUSE_SCROLL = 3
    MOUSE_MOVE = 4
    KEY = 5


_ENUM_CONST = {
    StepEnum.ACTIVE_WAIT: ('image: url(:/images/images/active_wait.png);\npadding:3px;', 'Active Wait Time'),
    StepEnum.MOUSE_LEFT: ('image: url(:/images/images/leftclick.png);\npadding:3px;', 'Mouse Left Click'),
    StepEnum.MOUSE_RIGHT: ('image: url(:/images/images/rightclick.png);\npadding:3px;', 'Mouse Right Click'),
    StepEnum.MOUSE_SCROLL: ('image: url(:/images/images/scroll.png);\npadding:3px;', 'Mouse Scroll'),
    StepEnum.MOUSE_MOVE: ('image: url(:/images/images/move.png);\npadding:3px;', 'Mouse Move'),
    StepEnum.KEY: ('image: url(:/images/images/keyboard.png);\npadding:3px;', 'Key Press'),
}

def stepImage(step):
    return _ENUM_CONST[step][0]

def stepDescriptor(step):
    return _ENUM_CONST[step][1]
