from enum import IntEnum

class OpCode(IntEnum):
    SYS_EXIT = 0
    SET_BRT  = 1
    LED_ON   = 2
    MV_MOTOR = 3
