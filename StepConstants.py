from enum import Enum

class StepEnum(Enum):
    ACTIVE_WAIT = 0
    INACTIVE_WAIT = 1
    MOUSE = 2
    KEY = 3

_ENUM_IMAGE = {
    StepEnum.ACTIVE_WAIT: 'image: url(:/images/images/plus.png);\npadding:3px;',
    StepEnum.INACTIVE_WAIT: 'image: url(:/images/images/plus.png);\npadding:3px;',
    StepEnum.MOUSE: 'image: url(:/images/images/plus.png);\npadding:3px;',
    StepEnum.KEY: 'image: url(:/images/images/plus.png);\npadding:3px;',
}

def stepImage(step):
    return _ENUM_IMAGE[step]
