from enum import Enum

class StepEnum(Enum):
    ACTIVE_WAIT = 0
    INACTIVE_WAIT = 1
    MOUSE_LEFT = 2
    MOUSE_RIGHT = 3
    MOUSE_SCROLL = 4
    KEY = 5


_ENUM_IMAGE = {
    StepEnum.ACTIVE_WAIT: 'image: url(:/images/images/active_wait.png);\npadding:3px;',
    StepEnum.INACTIVE_WAIT: 'image: url(:/images/images/inactive_wait.png);\npadding:3px;',
    StepEnum.MOUSE_LEFT: 'image: url(:/images/images/leftclick.png);\npadding:3px;',
    StepEnum.MOUSE_RIGHT: 'image: url(:/images/images/rightclick.png);\npadding:3px;',
    StepEnum.MOUSE_SCROLL: 'image: url(:/images/images/scroll.png);\npadding:3px;',
    StepEnum.KEY: 'image: url(:/images/images/keyboard.png);\npadding:3px;',
}

def stepImage(step):
    return _ENUM_IMAGE[step]
