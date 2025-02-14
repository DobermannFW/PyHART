import threading


class STEP_RX:
    STEP_PREAMBLES = 0
    STEP_DELIMITER = 1
    STEP_SHORT_ADDRESS = 2
    STEP_LONG_ADDRESS = 3
    STEP_EXPANSION = 4
    STEP_COMMAND = 5
    STEP_DATA_LEN = 6
    STEP_RESPONSE_CODE = 7
    STEP_DEVICE_STATUS = 8
    STEP_DATA = 9
    STEP_CHECKSUM = 10


class PacketType:
    NONE = 0
    STX = 1
    ACK = 2
    OSTX = 3
    OACK = 4
    BACK = 5
    OBACK = 6

    
class MASTER_TYPE:
    PRIMARY = 0
    SECONDARY = 1


class CommResult:
    Ok = 0
    NoResponse = 1
    ChecksumError = 2
    FrameError = 3
    Sync = 4


class HART_REVISION:
    FIVE = 5
    SIX = 6
    SEVEN = 7


globalPrintActivityLock = threading.RLock()

