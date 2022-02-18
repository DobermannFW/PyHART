###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
import sys
import serial
import threading
from datetime import datetime
import time
from PyHART.COMMUNICATION.Packet import HartPacket
from PyHART.COMMUNICATION.Device import HartDevice
from PyHART.COMMUNICATION.Utils import *
from PyHART.COMMUNICATION.Common import *


class Logger:
    def __init__(self, whereToPrint, logFile):
        self.terminal = sys.stdout
        self.whereToPrint = whereToPrint
        self.terminalLock = threading.Lock()
        
        if (logFile is not None) and ((whereToPrint == WhereToPrint.BOTH) or (whereToPrint == WhereToPrint.FILE)):
            self.log = open(logFile, "a")
            self.writeFile("\n:::::::::::::::::::: New Log Session : {0} ::::::::::::::::::::\n".format(datetime.now()))

    def write(self, message):
        self.terminalLock.acquire()
        if (self.whereToPrint == WhereToPrint.BOTH):
            self.terminal.write(message)
            self.writeFile(message)
        elif (self.whereToPrint == WhereToPrint.FILE):
            self.writeFile(message)
        elif (self.whereToPrint == WhereToPrint.TERMINAL):
            self.terminal.write(message)
        self.terminalLock.release()

    def writeFile(self, message):
        self.log.write(message)  
        self.log.flush()

    def flush(self):
        self.terminal.flush()    

    
class MASTER_STATUS:
    WATCHING = 0
    ENABLED = 1
    USING = 2
    
class MASTER_TIMERS:
    NONE = 0
    RT1 = 1
    RT2 = 2

class WhereToPrint:
    BOTH = 0
    TERMINAL = 1
    FILE = 2
    
class Events:
    OnCommDone = 0
    OnFrameSent = 1

class CommunicationDoneEventArgs:
    def __init__(self, _rxPacket, _CommunicationResult, _packetType, _stepRx, _currtime):        
        if (_rxPacket != None):
            self.rxPacket = _rxPacket.Clone()
        else:
            self.rxPacket = None

        self.CommunicationResult = _CommunicationResult
        self.packetType = _packetType
        self.stepRx = _stepRx
        self.currtime = _currtime

class FrameSentEventArgs:
    def __init__(self, _txPacket, _currtime):
        self.txPacket = _txPacket.Clone()
        self.currtime = _currtime

class HartMaster:
    def __init__(self, port, masterType = None, num_retry = None, retriesOnPolling = None, autoPrintTransactions = None, whereToPrint = None, logFile = None, rt_os = None, manageRtsCts = None):
        
        self.TIME_OUT = 3
        self.BYTE_TIME = 0.00916666667
        
        if (num_retry == None):
            self.RETRY_COUNT = 3
        else:
            self.RETRY_COUNT = num_retry
            
        self._numberOfRetries = self.RETRY_COUNT
        
        if (retriesOnPolling == None):
            self._retriesOnPolling = True
        else:
            self._retriesOnPolling = retriesOnPolling
            
        if (whereToPrint == None):
            self.whereToPrint = WhereToPrint.TERMINAL
        else:
            self.whereToPrint = whereToPrint            
        
        sys.stdout = Logger(self.whereToPrint, logFile)
        
        if (autoPrintTransactions == None):
            self.autoPrintTransactions = True
        else:
            self.autoPrintTransactions = autoPrintTransactions
        """
        if (self.autoPrintTransactions == True):
            print("\n")
            print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print("::::::                            PyHART                                 ::::::")
            print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print("\n")
        """
        self.CommunicationResult = CommResult.NoResponse
        self.RecvPacket = None
        
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
                
        self._serial.inter_byte_timeout = 0.00916666667
        self._serial.rts = False
        
        self.NetworkMonitorIsAlive = None
        self.OnResponseOrTimeout = None
        self.monitorThread = None
        
        self.RT1p_time = 0.303
        self.RT1s_time = 0.376
        self.RT2_time = 0.073
        
        self.CanAccessNetwork = None
        self.CanAccessFlag = False
        
        if (self.runningOnRTOS == True):
            self.TIME_OUT = self.RT1p_time
            
        self.CommunicationResult = None
        self.SentPacket = None
        self.RecvPacket = None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def Start(self):        
        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
        self._serial.open()
        self.OnResponseOrTimeout = threading.Event()
        self.OnResponseOrTimeout.clear()
        self.NetworkMonitorIsAlive = threading.Event()
        self.NetworkMonitorIsAlive.clear()
        self.monitorThread = threading.Thread(target = self.NetworkMonitor)
        self.monitorThread.daemon = True
        self.NetworkMonitorIsAlive.set()
        self.monitorThread.start()
        
        self.CanAccessNetwork = threading.Event()
        self.CanAccessNetwork.clear()
        self.CanAccessFlag = False
        
        self.networkIsInBurst = False
        self.masterStatus = MASTER_STATUS.WATCHING
        self.RT1 = None
        self.RT2 = None
        self.runningTimer = MASTER_TIMERS.NONE
        
    def Stop(self):          
        if self.monitorThread is not None:            
            self.NetworkMonitorIsAlive.clear()
            self.monitorThread.join()
            self.monitorThread = None
        
        self.OnlineDevice = None
        if self._serial is not None:
            self._serial.close()
        
        self._serial = None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def PrintMsg(self, evtType, evtArgs):
        if (evtType == Events.OnCommDone):
            if ((evtArgs.CommunicationResult == CommResult.Ok) or (evtArgs.CommunicationResult == CommResult.ChecksumError)):                            
                if (evtArgs.packetType == PacketType.ACK):
                    if (self.autoPrintTransactions == True):
                        print('')
                        print("[SLAVE TO MASTER - ACK] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                        
                elif (evtArgs.packetType == PacketType.OACK):
                    if (self.autoPrintTransactions == True):
                        print('', 'white')
                        print("[SLAVE TO MASTER - OACK] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                    
                elif (evtArgs.packetType == PacketType.BACK):
                    if (self.autoPrintTransactions == True):
                        print('')
                        print("[BURST FRAME - BACK] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                        
                elif (evtArgs.packetType == PacketType.OBACK):
                    if (self.autoPrintTransactions == True):
                        print('')
                        print("[BURST FRAME - OBACK] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                    
                elif (evtArgs.packetType == PacketType.STX):
                    if (self.autoPrintTransactions == True):
                        print('')
                        print("[MASTER TO SLAVE - STX] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                    
                elif (evtArgs.packetType == PacketType.OSTX):
                    if (self.autoPrintTransactions == True):
                        print('')
                        print("[MASTER TO SLAVE - OSTX] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                    
                else:
                    if (self.autoPrintTransactions == True):
                        print('', 'white')
                        print("[UNKNOWN PACKET] - {0}".format(evtArgs.currtime))
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                
                if (evtArgs.CommunicationResult == CommResult.ChecksumError):
                    if (self.autoPrintTransactions == True):
                        print ("- CHECKSUM ERROR -")
                        
                if (self.autoPrintTransactions == True):
                    print("\n")
                
            elif (evtArgs.CommunicationResult == CommResult.FrameError):
                if (self.autoPrintTransactions == True):
                    print('')
                    print("[FRAME ERROR] - {0}".format(evtArgs.currtime))
                    evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                    print("\n")
                    
            elif (evtArgs.CommunicationResult == CommResult.NoResponse):
                if (self.autoPrintTransactions == True):
                    print('')
                    print("[NO RESPONSE RECEIVED] - {0}".format(evtArgs.currtime))
                    print("\n")
                    
            elif (evtArgs.CommunicationResult == CommResult.Sync):
                if (self.autoPrintTransactions == True):
                    print('')
                    print("[SYNCHRONIZING ON PREAMBLES] - {0}".format(evtArgs.currtime))
                    evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice)
                    print("\n")
        
        elif (evtType == Events.OnFrameSent):
            if (self.autoPrintTransactions == True):
                print('')
                print("[MASTER TO SLAVE - STX] - {0}".format(evtArgs.currtime))
                evtArgs.txPacket.printPkt(STEP_RX.STEP_CHECKSUM, self.OnlineDevice)
                print("\n")
    
    def SendCommdoneEvent(self):
        if (self.runningOnRTOS == True):
            if (self._commRes == CommResult.FrameError) or (self._commRes == CommResult.Sync):
                self.masterStatus = MASTER_STATUS.WATCHING
            
                if (self.runningTimer == MASTER_TIMERS.RT1):
                    self.RT1.cancel()
                
                if (self.runningTimer == MASTER_TIMERS.RT2):
                    self.RT2.cancel()

                self.runningTimer = MASTER_TIMERS.NONE
            
                self.CanAccessFlag = False
                
                if (self.CanAccessNetwork.is_set() == False):
                    self.CanAccessNetwork.set()
        
        self.CommunicationResult = self._commRes
        self.RecvPacket = self._rxPacket
        
        evtArgs = CommunicationDoneEventArgs(self._rxPacket, self._commRes, self._packetType, self._decodeResponseStep, datetime.now(tz=None))
        self.PrintMsg(Events.OnCommDone, evtArgs)
        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES

    def SendFramesentEvent(self, txPacket):
        evtArgs = FrameSentEventArgs(txPacket, datetime.now(tz=None))        
        self.PrintMsg(Events.OnFrameSent, evtArgs)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
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
                        self._rxPacket = HartPacket()
                        
                        self._rxPacket.preamblesCnt += 1

                        if (rxByte == HartPacket.PREAMBLE):
                            self._decodeResponseStep = STEP_RX.STEP_DELIMITER
                        else:
                            self._decodeResponseStep = STEP_RX.STEP_DELIMITER
                            self._rxPacket.preamblesCnt = 0;
                            self._rxPacket.delimiter = rxByte
                            self._commRes = CommResult.Sync
                            self.SendCommdoneEvent()

                    elif (self._decodeResponseStep == STEP_RX.STEP_DELIMITER):
                        if ((rxByte == HartPacket.PREAMBLE) and (self._rxPacket.preamblesCnt <= HartPacket.MAX_PREAMBLE_NUM)):
                            self._rxPacket.preamblesCnt += 1
                            
                        elif ((rxByte == HartPacket.PREAMBLE) and (self._rxPacket.preamblesCnt > HartPacket.MAX_PREAMBLE_NUM)):
                            self._rxPacket.preamblesCnt += 1
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                            self._commRes = CommResult.Sync
                            self.SendCommdoneEvent()
                                
                        elif (rxByte != HartPacket.PREAMBLE):
                            self._rxPacket.delimiter = rxByte
                            if (self._rxPacket.preamblesCnt >= HartPacket.MIN_PREAMBLE_NUM):
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
                        else:
                            if (self.masterType == MASTER_TYPE.PRIMARY):
                                if ((rxByte & 0x80) == 0):
                                    self._packetType = PacketType.OBACK
                            else:
                                if ((rxByte & 0x80) > 0):
                                    self._packetType = PacketType.OBACK

                        self._rxPacket.address[0] = rxByte

                        if (self._rxPacket.getExpansionBytesCount() > 0):
                            self._decodeResponseStep = STEP_RX.STEP_EXPANSION
                        else:
                            self._decodeResponseStep = STEP_RX.STEP_COMMAND
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_LONG_ADDRESS):
                        if (self._cnt < HartPacket.ADDR_SIZE):
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
                            else:
                                if (self.masterType == MASTER_TYPE.PRIMARY):
                                    if ((rxByte & 0x80) == 0):
                                        self._packetType = PacketType.OBACK
                                else:
                                    if ((rxByte & 0x80) > 0):
                                        self._packetType = PacketType.OBACK

                        if (self._cnt == (HartPacket.ADDR_SIZE - 1)):
                            if (((self._rxPacket.address[0] & 0x3F) | self._rxPacket.address[1] | self._rxPacket.address[2] | self._rxPacket.address[3] | self._rxPacket.address[4]) > 0):
                                if (self.OnlineDevice != None):
                                    if ((self.OnlineDevice.hartRev == HART_REVISION.FIVE) or (self.OnlineDevice.hartRev == HART_REVISION.SIX)):
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
                        elif (self._cnt >= HartPacket.ADDR_SIZE):
                            self._rxPacket.command = rxByte
                            self._commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                        else:
                            self._cnt += 1
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_EXPANSION):
                        if (self._cnt < HartPacket.EXT_SIZE):
                            self._rxPacket.expansionBytes[self._cnt] = rxByte

                        if (self._cnt == (HartPacket.EXT_SIZE - 1)):
                            self._cnt = 0
                            self._decodeResponseStep = STEP_RX.STEP_COMMAND
                        elif (self._cnt >= HartPacket.EXT_SIZE):
                            self._rxPacket.command = rxByte
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
                            if ((self._rxPacket.command == HartPacket.LONG_COMMAND_INDICATOR) and ((self.OnlineDevice.hartRev == HART_REVISION.SIX) or (self.OnlineDevice.hartRev == HART_REVISION.SEVEN))):
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
                        if (self._cnt < HartPacket.DATA_SIZE):
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

                        if (self._cnt >= HartPacket.DATA_SIZE):
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
                            
                        if (self.runningOnRTOS == True): 
                            self.SendCommdoneEvent()
                            
                            if (self._packetType == PacketType.ACK):
                                if (self.masterStatus == MASTER_STATUS.USING):
                                    self.StopTimers()
                                    self.masterStatus = MASTER_STATUS.WATCHING
                                    if (self.networkIsInBurst == False):
                                        self.StartRT2Timer()
                                    else:
                                        self.StartRT1Timer(False)
                                    
                                    if ((self._commRes == CommResult.Ok) and (self._rxPacket.command == 0) and (self._rxPacket.resCode == 0) and (self._rxPacket.isLongAddressPacket() == False)):
                                        self.OnlineDevice = HartDevice()
                                        self.OnlineDevice.Fill(self._rxPacket, self.masterType)
                                    
                                    if (self.OnResponseOrTimeout.is_set() == False):
                                        self.OnResponseOrTimeout.set()

                            elif (self._packetType == PacketType.OACK):
                                if (self.networkIsInBurst == False):
                                    if (self.masterStatus == MASTER_STATUS.WATCHING):
                                        self.BecameTokenHandler()
                                        
                                    elif (self.masterStatus == MASTER_STATUS.USING):
                                        self.ManageUsingStatusWhenMessageIsNotForMe()
                                else:
                                    if (self.masterStatus == MASTER_STATUS.WATCHING):
                                        self.CannotBecameTokenHandler(False)
                                        
                                    elif (self.masterStatus == MASTER_STATUS.USING):
                                        self.ManageUsingStatusWhenMessageIsNotForMe()
                                        
                            elif (self._packetType == PacketType.BACK):
                                self.networkIsInBurst = True
                                if (self.masterStatus == MASTER_STATUS.WATCHING):
                                    self.CannotBecameTokenHandler(False)
                                    
                                elif (self.masterStatus == MASTER_STATUS.USING):
                                    self.ManageUsingStatusWhenMessageIsNotForMe()

                            elif (self._packetType == PacketType.OBACK):
                                self.networkIsInBurst = True
                                if (self.masterStatus == MASTER_STATUS.WATCHING):
                                    self.BecameTokenHandler()
                                    
                                elif (self.masterStatus == MASTER_STATUS.USING):
                                    self.ManageUsingStatusWhenMessageIsNotForMe()

                            elif (self._packetType == PacketType.OSTX):
                                if (self.networkIsInBurst == False):
                                    if (self.masterStatus == MASTER_STATUS.WATCHING):
                                        self.CannotBecameTokenHandler(False)
                                        
                                    elif (self.masterStatus == MASTER_STATUS.USING):
                                        self.ManageUsingStatusWhenMessageIsNotForMe()
                                else:
                                    if (self.masterStatus == MASTER_STATUS.WATCHING):
                                        self.CannotBecameTokenHandler(True)
                                        
                                    elif (self.masterStatus == MASTER_STATUS.USING):
                                        self.ManageUsingStatusWhenMessageIsNotForMe()

                        else:                           
                            
                            if (self._packetType == PacketType.ACK):
                                if (self.OnResponseOrTimeout != None):
                                    if ((self._commRes == CommResult.Ok) and (self._rxPacket.command == 0) and (self._rxPacket.resCode == 0) and (self._rxPacket.isLongAddressPacket() == False)):
                                        self.OnlineDevice = HartDevice()
                                        self.OnlineDevice.Fill(self._rxPacket, self.masterType)
                                    self.SendCommdoneEvent()
                                    self.OnResponseOrTimeout.set()
                                else:
                                    self.SendCommdoneEvent()
                            else:
                                self.SendCommdoneEvent()

                        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def ManageUsingStatusWhenMessageIsNotForMe(self):
        self.StopTimers()        
        self.masterStatus = MASTER_STATUS.WATCHING
        
        if (self.OnResponseOrTimeout.is_set() == False):
            self._commRes = CommResult.NoResponse
            self.OnResponseOrTimeout.set()
            
    def CannotBecameTokenHandler(self, doubleTime):
        self.StopTimers()     
        self.masterStatus = MASTER_STATUS.WATCHING
        self.StartRT1Timer(doubleTime)

    def BecameTokenHandler(self):
        self.StopTimers()
        self.runningTimer = MASTER_TIMERS.NONE
        self.MasterCanAccessNetwork()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def SetOnlineDevice(self, device):
        self.OnlineDevice = device
        
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def StopTimers(self):
        if (self.runningTimer == MASTER_TIMERS.RT1):
            self.RT1.cancel()
        elif (self.runningTimer == MASTER_TIMERS.RT2):
            self.RT2.cancel()
            
        self.runningTimer = MASTER_TIMERS.NONE
    
    def ManageRT1time(self, interval, doubleTime):
        if (doubleTime == False):
            self.RT1 = threading.Timer(interval, self.RT1Expired)
            self.RT1.start()
        else:
            self.RT1 = threading.Timer(interval * 2, self.RT1Expired)
            self.RT1.start()
    
    def StartRT1Timer(self, doubleTime):
        self.runningTimer = MASTER_TIMERS.RT1
        
        if (self.masterType == MASTER_TYPE.PRIMARY):
            self.ManageRT1time(self.RT1p_time, doubleTime)
        else:
            self.ManageRT1time(self.RT1s_time, doubleTime)
        
    def StartRT2Timer(self):
        self.runningTimer = MASTER_TIMERS.RT2
        self.RT2 = threading.Timer(self.RT2_time, self.RT2Expired)
        self.RT2.start()
    
    def RT2Expired(self):
        self.runningTimer = MASTER_TIMERS.NONE
        if (self.masterStatus == MASTER_STATUS.WATCHING):
            self.networkIsInBurst = False
            self.MasterCanAccessNetwork()
    
    def RT1Expired(self):
        self.runningTimer = MASTER_TIMERS.NONE
    
        if (self.masterStatus == MASTER_STATUS.WATCHING):
            self.networkIsInBurst = False
            self.MasterCanAccessNetwork()
            
        elif (self.masterStatus == MASTER_STATUS.USING):
            self.masterStatus = MASTER_STATUS.WATCHING
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
            self.OnResponseOrTimeout.set()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def CanRetry(self):
        if (self._numberOfRetries > 0):
            if (self._numberOfRetries < self.RETRY_COUNT):
                # for retries let time to field device...
                #print("-------------------------------------------------------------------------------")
                print("[ !!! RETRY !!! ]")
                time.sleep(0.5)
                
            self._numberOfRetries -= 1
            
            return True
        else:
            # for retries let time to field device...
            time.sleep(0.5)
            return False
            
    def PerformTransaction(self, command, Data):
        commRes = CommResult.NoResponse
        self._numberOfRetries = self.RETRY_COUNT
        txPkt = None
        rxPkt = None
        while ((commRes != CommResult.Ok) and self.CanRetry()):
            if (Data is not None):
                dataLen = len(Data)
            else:
                dataLen = 0
            
            commRes, txPkt, rxPkt = self.SendCmd(command, Data, dataLen, False)
            
        return commRes, txPkt, rxPkt
        
    def PerformBroadcastTransaction(self, command, Data):
        commRes = CommResult.NoResponse
        self._numberOfRetries = self.RETRY_COUNT
        txPkt = None
        rxPkt = None
        while ((commRes != CommResult.Ok) and self.CanRetry()):
            if (Data is not None):
                dataLen = len(Data)
            else:
                dataLen = 0
            
            commRes, txPkt, rxPkt = self.SendCmd(command, Data, dataLen, True)
            
        return commRes, txPkt, rxPkt
                
    def SendCustomFrame(self, txFrame):
        commRes = CommResult.NoResponse
        self._numberOfRetries = self.RETRY_COUNT
        txPkt = None
        rxPkt = None
        while ((commRes != CommResult.Ok) and self.CanRetry()):
            commRes, txPkt, rxPkt = self.SendFrm(txFrame)
        
        return commRes, txPkt, rxPkt
                
    def LetKnowDevice(self, pollAddr):        
        txPkt = None
        rxPkt = None
        if (self._retriesOnPolling == False):
            commRes, txPkt, rxPkt, device = self.SendShortCommandZero(pollAddr)            
        else:
            commRes = CommResult.NoResponse
            self._numberOfRetries = self.RETRY_COUNT
            while ((commRes != CommResult.Ok) and self.CanRetry()):
                commRes, txPkt, rxPkt, device = self.SendShortCommandZero(pollAddr)
        
        return commRes, txPkt, rxPkt, device
        
        
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def WaitForResponseNoRTOS(self):
        event_is_set = self.OnResponseOrTimeout.wait(self.TIME_OUT)
        if (event_is_set == False):
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
        
        self.OnResponseOrTimeout.clear()
        
    def WaitForResponseRTOS(self):
        self.OnResponseOrTimeout.wait()
        self.OnResponseOrTimeout.clear()
        
    def SendCmd(self, command, Data, DataLen, UseBroadcastAddress):
        txPacket = None
        if (self.OnlineDevice != None):
            txPacket = HartPacket()
            txPacket.PrepareTxPacket(self.OnlineDevice, self.masterType, False, self.OnlineDevice.pollAddr, Data, DataLen, command, UseBroadcastAddress)
            txFrame = txPacket.ToFrame()
            
            self.WriteOnSerial(txFrame, len(txFrame))
            self.SendFramesentEvent(txPacket)

            if (self.runningOnRTOS == False):
                self.WaitForResponseNoRTOS()
            else:
                self.WaitForResponseRTOS()
        else:
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
   
        return self.CommunicationResult, txPacket, self.RecvPacket

    def SendFrm(self, txFrame):
        self.WriteOnSerial(txFrame, len(txFrame))
        
        txPacket = HartPacket()
        txPacket.FillFromTxFrame(txFrame)
        self.SendFramesentEvent(txPacket)

        if (self.runningOnRTOS == False):
            self.WaitForResponseNoRTOS()
        else:
            self.WaitForResponseRTOS()
        
        return self.CommunicationResult, txPacket, self.RecvPacket

    def SendShortCommandZero(self, pollAddr):
        txPacket = HartPacket()
        txPacket.PrepareTxPacket(None, self.masterType, True, pollAddr, None, 0, 0, False)
        txFrame = txPacket.ToFrame()
        
        self.WriteOnSerial(txFrame, len(txFrame))
        self.SendFramesentEvent(txPacket)
        
        if (self.runningOnRTOS == False):
            self.WaitForResponseNoRTOS()
        else:
            self.WaitForResponseRTOS()
 
        return self.CommunicationResult, txPacket, self.RecvPacket, self.OnlineDevice

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    def TransmitMessage(self, buffer, len):
        self.masterStatus = MASTER_STATUS.ENABLED
        txTime = self.BYTE_TIME * len
        self._serial.rts = True
        self._serial.write(buffer)
        time.sleep(txTime)
        self._serial.rts = False
        self.masterStatus = MASTER_STATUS.USING
        
    def WaitForTransmission(self, buffer, len):
        self.CanAccessNetwork.wait()
        self.CanAccessNetwork.clear()
        
        if (self.CanAccessFlag == True):
            self.TransmitMessage(buffer, len)
            self.StartRT1Timer(False)
            
    def MasterCanAccessNetwork(self):
        if (self.CanAccessNetwork.is_set() == False):
            self.CanAccessFlag = True
            self.CanAccessNetwork.set()
            
    def WriteOnSerial(self, buffer, len):
        if (self.runningOnRTOS == True):
            self.CanAccessFlag = False
        
            if (self.runningTimer == MASTER_TIMERS.NONE):                
                self.masterStatus = MASTER_STATUS.WATCHING
                self.StartRT1Timer(False)
                
                self.WaitForTransmission(buffer, len)
            
            elif ((self.runningTimer == MASTER_TIMERS.RT2) or (self.runningTimer == MASTER_TIMERS.RT1)) and (self.masterStatus == MASTER_STATUS.WATCHING):
                self.WaitForTransmission(buffer, len)
            
        else:
            if (self._serial.rtscts == True):
                self._serial.rts = True
                time.sleep(self.BYTE_TIME) # Wait that RTS has really been set before to send the frame.

            self._serial.write(buffer)
            self._serial.flush()
            
            if (self._serial.rtscts == True):
                # flush is not enaugh. Better to wait a while before to clear RTS.
                # This ensure that all frame bytes have been sent.
                time.sleep(self.BYTE_TIME * 2)
                self._serial.rts = False
