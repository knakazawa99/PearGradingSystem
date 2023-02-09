from enum import IntEnum

class RpiRes(IntEnum):
    ACK = 0
    NAK = 1
    ERR = 2


class RxIndex(IntEnum):
    ACK      = 0
    ERROR    = 1
    HOME_END = 2
    IN_POS   = 3
    READY    = 4
    MOVE     = 5
    ALM_B    = 6

class TableRot(IntEnum):
    ZHOME = 0
    DEG_PER_120 = 1