###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
from enum import IntEnum
import Packet
import Device
import Utils
import serial
import threading
import queue
import datetime
import time

class STEP_RX(IntEnum):
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

class PacketType(IntEnum):
    NONE = 0
    STX = 1
    OSTX = 2
    OACK = 3
    BACK = 4
    ACK = 5
    
class MASTER_TYPE(IntEnum):
    PRIMARY = 0
    SECONDARY = 1

class CommResult(IntEnum):
    Ok = 0
    NoResponse = 1
    ChecksumError = 2
    FrameError = 3
    Sync = 4

class Events(IntEnum):
    OnCommDone = 0
    OnFrameSent = 1

class CommunicationDoneEventArgs():
    def __init__(self, _rxPacket, _CommunicationResult, _packetType, _stepRx, _currtime):        
        if (_rxPacket != None):
            self.rxPacket = _rxPacket.Clone()
        else:
            self.rxPacket = None

        self.CommunicationResult = _CommunicationResult
        self.packetType = _packetType
        self.stepRx = _stepRx
        self.currtime = _currtime

class FrameSentEventArgs():
    def __init__(self, _txPacket, _currtime):
        self.txPacket = _txPacket.Clone()
        self.currtime = _currtime

class HartComm():
    def __init__(self, port, masterType = None, rt_os = None, manageRtsCts = None):
        self.TIME_OUT = 1.5
        
        if (masterType == None):
            self.masterType = MASTER_TYPE.PRIMARY
        else:
            self.masterType = masterType
            
        if (rt_os == None):
            self.runningOnRTOS = False
        else:
            self.runningOnRTOS = rt_os
        
        self._packetType = PacketType.NONE
        self._commRes = CommResult.Ok
        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
        self._cnt = 0
        self._rxPacket = None
        self.OnlineDevice = None
        
        self._serial = serial.Serial()
        self._serial.port = port
        self._serial.baudrate = 1200
        self._serial.parity = serial.PARITY_ODD
        self._serial.stopbits = serial.STOPBITS_ONE
        self._serial.bytesize = 8 
        self._serial.xonxoff = False
        
        if (manageRtsCts == None):
            self._serial.rtscts = False
        else:
            if (manageRtsCts == True):
                self._serial.rtscts = True
            else:
                self._serial.rtscts = False
                
        self._serial.inter_byte_timeout= 0.00916666667
        self._serial.rts = False
        
        self.NetworkMonitorIsAlive = None
        self.OnResponseOrTimeout = None
        self.EvtQueue = queue.Queue(maxsize=0)
        self.monitorThread = None

    def Open(self):
        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
        self._serial.open()
        self.OnResponseOrTimeout = threading.Event()
        self.NetworkMonitorIsAlive = threading.Event()
        self.monitorThread = threading.Thread(target = self.NetworkMonitor)
        self.monitorThread.daemon = True
        self.NetworkMonitorIsAlive.set()
        self.monitorThread.start()
        
    def Close(self):        
        if self.monitorThread is not None:            
            self.NetworkMonitorIsAlive.clear()
            self.monitorThread.join()
            self.monitorThread = None
        
        self.OnlineDevice = None
        
        self._serial.close()
        self.ClearQueues()            
        
    def ClearQueues(self):
        while (self.EvtQueue.empty() == False):
            self.EvtQueue.get()
    
    def SendCommdoneEvent(self):
        evtArgs = CommunicationDoneEventArgs(self._rxPacket, self._commRes, self._packetType, self._decodeResponseStep, datetime.datetime.now(tz=None))
        self.EvtQueue.put([Events.OnCommDone, evtArgs])
        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES

    def SendFramesentEvent(self, txPacket):
        evtArgs = FrameSentEventArgs(txPacket, datetime.datetime.now(tz=None))
        self.EvtQueue.put([Events.OnFrameSent, evtArgs])

    def NetworkMonitor(self):
        while self.NetworkMonitorIsAlive.is_set():
            buffer = None
            buffer = self._serial.read(self._serial.in_waiting)

            if (buffer):
                for i in range(len(buffer)):
                    rxByte = buffer[i]
                    
                    if (self._decodeResponseStep == STEP_RX.STEP_PREAMBLES):
                        self._commRes = CommResult.Ok
                        self._packetType = PacketType.NONE
                        self._cnt = 0
                        self._rxPacket = Packet.HartPacket()
                        
                        self._rxPacket.preamblesCnt += 1

                        if (rxByte == Packet.PREAMBLE):
                            self._decodeResponseStep = STEP_RX.STEP_DELIMITER
                        else:
                            self._decodeResponseStep = STEP_RX.STEP_DELIMITER
                            self._rxPacket.preamblesCnt = 0;
                            self._rxPacket.delimiter = rxByte
                            self._commRes = CommResult.Sync
                            self.SendCommdoneEvent()

                    elif (self._decodeResponseStep == STEP_RX.STEP_DELIMITER):
                        if ((rxByte == Packet.PREAMBLE) and (self._rxPacket.preamblesCnt <= Packet.MAX_PREAMBLE_NUM)):
                            self._rxPacket.preamblesCnt += 1
                            
                        elif ((rxByte == Packet.PREAMBLE) and (self._rxPacket.preamblesCnt > Packet.MAX_PREAMBLE_NUM)):
                            self._rxPacket.preamblesCnt += 1
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                            self._commRes = CommResult.Sync
                            self.SendCommdoneEvent()
                                
                        elif (rxByte != Packet.PREAMBLE):
                            self._rxPacket.delimiter = rxByte
                            if (self._rxPacket.preamblesCnt >= Packet.MIN_PREAMBLE_NUM):
                                if (self._rxPacket.isTxPacket()):
                                    self._packetType = PacketType.STX
                                else:
                                    if (self._rxPacket.isBurstPacket()):
                                        self._packetType = PacketType.BACK
                                    else:
                                        self._packetType = PacketType.ACK

                                if (self._rxPacket.isLongAddressPacket()):
                                    self._decodeResponseStep = STEP_RX.STEP_LONG_ADDRESS
                                else:
                                    self._decodeResponseStep = STEP_RX.STEP_SHORT_ADDRESS
                            else:
                                self._commRes = CommResult.Sync
                                self.SendCommdoneEvent()
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_SHORT_ADDRESS):
                        if (self._packetType != PacketType.BACK):
                            if (self.masterType == MASTER_TYPE.PRIMARY):
                                if ((rxByte & 0x80) == 0):
                                    if (self._rxPacket.isTxPacket()):
                                        self._packetType = PacketType.OSTX
                                    else:
                                        self._packetType = PacketType.OACK
                            else:
                                if ((rxByte & 0x80) > 0):
                                    if (self._rxPacket.isTxPacket()):
                                        self._packetType = PacketType.OSTX
                                    else:
                                        self._packetType = PacketType.OACK

                        self._rxPacket.address[0] = rxByte

                        if (self._rxPacket.getExpansionBytesCount() > 0):
                            self._decodeResponseStep = STEP_RX.STEP_EXPANSION
                        else:
                            self._decodeResponseStep = STEP_RX.STEP_COMMAND
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_LONG_ADDRESS):
                        if (self._cnt < Packet.ADDR_SIZE):
                            self._rxPacket.address[self._cnt] = rxByte

                        if (self._cnt == 0):
                            if (self._packetType != PacketType.BACK):
                                if (self.masterType == MASTER_TYPE.PRIMARY):
                                    if ((rxByte & 0x80) == 0):
                                        if (self._rxPacket.isTxPacket()):
                                            self._packetType = PacketType.OSTX
                                        else:
                                            self._packetType = PacketType.OACK
                                else:
                                    if ((rxByte & 0x80) > 0):
                                        if (self._rxPacket.isTxPacket()):
                                            self._packetType = PacketType.OSTX
                                        else:
                                            self._packetType = PacketType.OACK

                        if (self._cnt == (Packet.ADDR_SIZE - 1)):
                            if (((self._rxPacket.address[0] & 0x3F) | self._rxPacket.address[1] | self._rxPacket.address[2] | self._rxPacket.address[3] | self._rxPacket.address[4]) > 0):
                                if (self.OnlineDevice != None):
                                    if ((self.OnlineDevice.hartRev == Device.HART_REVISION.FIVE) or (self.OnlineDevice.hartRev == Device.HART_REVISION.SIX)):
                                        if (((self._rxPacket.address[0] & 0x3F) != (self.OnlineDevice.manufacturerId & 0x003F)) or (self._rxPacket.address[1] != ((self.OnlineDevice.deviceType & 0x00FF))) or (self._rxPacket.address[2] != self.OnlineDevice.uid[0]) or (self._rxPacket.address[3] != self.OnlineDevice.uid[1]) or (self._rxPacket.address[4] != self.OnlineDevice.uid[2])):
                                            self._commRes = CommResult.FrameError
                                            self.SendCommdoneEvent()
                                    else:
                                        if (((self._rxPacket.address[0] & 0x3F) != ((self.OnlineDevice.deviceType & 0x3F00) >> 8)) or (self._rxPacket.address[1] != ((self.OnlineDevice.deviceType & 0x00FF))) or (self._rxPacket.address[2] != self.OnlineDevice.uid[0]) or (self._rxPacket.address[3] != self.OnlineDevice.uid[1]) or (self._rxPacket.address[4] != self.OnlineDevice.uid[2])):
                                            self._commRes = CommResult.FrameError
                                            self.SendCommdoneEvent()

                            if (self._rxPacket.getExpansionBytesCount() > 0):
                                self._decodeResponseStep = STEP_RX.STEP_EXPANSION
                            else:
                                self._decodeResponseStep = STEP_RX.STEP_COMMAND

                            self._cnt = 0
                        elif (self._cnt >= Packet.ADDR_SIZE):
                            self._rxPacket.command = rxByte
                            self._commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                        else:
                            self._cnt += 1
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_EXPANSION):
                        if (self._cnt < Packet.EXT_SIZE):
                            self._rxPacket.expansionBytes[self._cnt] = rxByte

                        if (self._cnt == (Packet.EXT_SIZE - 1)):
                            self._cnt = 0
                            self._decodeResponseStep = STEP_RX.STEP_COMMAND
                        elif (self._cnt >= Packet.EXT_SIZE):
                            _rxPacket.command = rxByte
                            _commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                        else:
                            self._cnt += 1
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_COMMAND):
                        self._rxPacket.command = rxByte
                        self._decodeResponseStep = STEP_RX.STEP_DATA_LEN
                        
                    elif (self._decodeResponseStep == STEP_RX.STEP_DATA_LEN):
                        self._rxPacket.dataLen = rxByte

                        if ((self._rxPacket.isTxPacket() == False) and (rxByte < 2)):
                            _commRes = CommResult.FrameError
                            self.SendCommdoneEvent()

                        if (self.OnlineDevice != None):
                            if ((self._rxPacket.command == Packet.LONG_COMMAND_INDICATOR) and ((self.OnlineDevice.hartRev == Device.HART_REVISION.SIX) or (self.OnlineDevice.hartRev == Device.HART_REVISION.SEVEN))):
                                if ((self._rxPacket.isTxPacket() == False) and (rxByte < 4)):
                                    self._commRes = CommResult.FrameError
                                    self.SendCommdoneEvent()
                                else:
                                    if (rxByte < 2):
                                        self._commRes = CommResult.FrameError
                                        self.SendCommdoneEvent()

                        if (self._rxPacket.isTxPacket() == False):
                            self._decodeResponseStep = STEP_RX.STEP_RESPONSE_CODE
                        else:
                            if (rxByte == 0x00):
                                self._decodeResponseStep = STEP_RX.STEP_CHECKSUM
                            else:
                                self._decodeResponseStep = STEP_RX.STEP_DATA
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_RESPONSE_CODE):
                        self._rxPacket.resCode = rxByte
                        self._decodeResponseStep = STEP_RX.STEP_DEVICE_STATUS
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_DEVICE_STATUS):
                        self._rxPacket.devStatus = rxByte

                        if (self._rxPacket.dataLen > 2):
                            self._decodeResponseStep = STEP_RX.STEP_DATA
                        else:
                            self._decodeResponseStep = STEP_RX.STEP_CHECKSUM
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_DATA):
                        if (self._cnt < Packet.DATA_SIZE):
                            self._rxPacket.data[self._cnt] = rxByte

                        if (self._rxPacket.isTxPacket()):
                            if (self._cnt == (self._rxPacket.dataLen - 1)):
                                self._cnt = 0
                                self._decodeResponseStep = STEP_RX.STEP_CHECKSUM
                            else:
                                self._cnt += 1
                        else:
                            if (self._cnt == ((self._rxPacket.dataLen - 1) - 2)):
                                self._cnt = 0
                                self._decodeResponseStep = STEP_RX.STEP_CHECKSUM
                            else:
                                self._cnt += 1

                        if (self._cnt >= Packet.DATA_SIZE):
                            self._rxPacket.checksum = rxByte
                            self._commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_CHECKSUM):
                        checksum = self._rxPacket.ComputeChecksum()
                        if (checksum != rxByte):
                            self._commRes = CommResult.ChecksumError
                        else:
                            self._commRes = CommResult.Ok

                        self._rxPacket.checksum = rxByte

                        if (self._packetType == PacketType.ACK):
                            if (self.OnResponseOrTimeout != None):
                                if ((self._commRes == CommResult.Ok) and (self._rxPacket.command == 0) and (self._rxPacket.resCode == 0) and (self._rxPacket.isLongAddressPacket() == False)):
                                    self.OnlineDevice = Device.HartDevice()
                                    self.OnlineDevice.Fill(self._rxPacket, self.masterType)
                                   
                                self.SendCommdoneEvent()
                                self.OnResponseOrTimeout.set()
                            else:
                                self.SendCommdoneEvent()
                        else:
                            self.SendCommdoneEvent()

                        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES

    def SendCommand(self, command, Data, DataLen):
        self.SendCmd(command, Data, DataLen, False)
        
    def SendBroadcastCommand(self, command, Data, DataLen):
        self.SendCmd(command, Data, DataLen, True)
                
    def SendFrame(self, txFrame):
        self.SendFrm(txFrame)
                
    def ReadUniqeId(self, pollAddr):
        self.SendShortCommandZero(pollAddr)
                
    def SendCmd(self, command, Data, DataLen, UseBroadcastAddress):
        if (self.OnlineDevice != None):
            txPacket = Packet.HartPacket()
            txPacket.PrepareTxPacket(self.OnlineDevice, self.masterType, False, self.OnlineDevice.pollAddr, Data, DataLen, command, UseBroadcastAddress)
            txFrame = txPacket.ToFrame()

            self.WriteOnSerial(txFrame, len(txFrame))
            self.SendFramesentEvent(txPacket)

            event_is_set = self.OnResponseOrTimeout.wait(self.TIME_OUT)
            if (event_is_set == False):
                self._commRes = CommResult.NoResponse
                self.SendCommdoneEvent()
            
            self.OnResponseOrTimeout.clear()
        else:
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
                    
    def SendFrm(self, txFrame):
        self.WriteOnSerial(txFrame, len(txFrame))
        
        txPacket = Packet.HartPacket()
        txPacket.FillFromTxFrame(txFrame)
        self.SendFramesentEvent(txPacket)

        event_is_set = self.OnResponseOrTimeout.wait(self.TIME_OUT)
        if (event_is_set == False):
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
                
        self.OnResponseOrTimeout.clear()

    def SendShortCommandZero(self, pollAddr):
        txPacket = Packet.HartPacket()
        txPacket.PrepareTxPacket(None, self.masterType, True, pollAddr, None, 0, 0, False)
        txFrame = txPacket.ToFrame()
        
        self.WriteOnSerial(txFrame, len(txFrame))

        self.SendFramesentEvent(txPacket)
        event_is_set = self.OnResponseOrTimeout.wait(self.TIME_OUT)
        if (event_is_set == False):
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
        
        self.OnResponseOrTimeout.clear()

    def WriteOnSerial(self, buffer, len):
        if (self.runningOnRTOS == True):
            txTime = 0.00916666667 * len
            self._serial.rts = True
            self._serial.write(buffer)
            time.sleep(txTime) # better than flush()! It close RTS immediatly after last sent bit.
        else:
            self._serial.rts = True
            self._serial.write(buffer)
            self._serial.flush()
            
        self._serial.rts = False

