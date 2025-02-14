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
        # In HartMaster faccio sys.stdout = Logger(...)
        # Ecco cosa avviene: prima viene istanziato l'oggetto di tipo Logger e poi viene eseguito l'assegnamento a sys.stdout di questo oggetto appena istanziato.
        # Quindi quando si istanzia l'oggetto di tipo Logger, viene fatto self.terminal = sys.stdout che è un backup dell'attuale sys.stdout in self.terminal.
        # Ora sys.stdout diventa l'istanza di logger. La print chiama sys.stdout.write che a questo punto si trova in questa classe.
        # Questa nuova write chiama la write di self.terminal che è lo standard output originale. inoltre scrive nel file ma soprattutto gestisce un oggetto lock.
        # Questo significa che ogni print chiamata dai vari thread è protetta dallo stesso lock object.
        # Il tutto evita di dover fare una funzione di scrittura apposta ma si può chiamare la print di python.
        self.terminal = sys.stdout
        self.whereToPrint = whereToPrint
        self.terminalLock = threading.Lock()
        self.log = None
        
        if (logFile is not None) and ((whereToPrint == WhereToPrint.BOTH) or (whereToPrint == WhereToPrint.FILE)):
            self.log = open(logFile, 'a')
            self.writeFile('\n:::::::::::::::::::: New Log Session : {0} ::::::::::::::::::::\n'.format(datetime.now()))

    def write(self, message):
        with self.terminalLock:
            if (self.whereToPrint == WhereToPrint.BOTH):
                self.terminal.write(message)
                self.writeFile(message)
            elif (self.whereToPrint == WhereToPrint.FILE):
                self.writeFile(message)
            elif (self.whereToPrint == WhereToPrint.TERMINAL):
                self.terminal.write(message)

    def writeFile(self, message):
        self.log.write(message)  
        self.log.flush()

    def flush(self):
        self.terminal.flush()    


class WhereToPrint:
    BOTH = 0
    TERMINAL = 1
    FILE = 2

    
class Events:
    OnCommDone = 0
    OnFrameSent = 1


class CommunicationDoneEventArgs:
    def __init__(self, a_rxPacket, _CommunicationResult, _packetType, _stepRx, _onlineDev):        
        if (a_rxPacket != None):
            self.rxPacket = a_rxPacket.Clone()
        else:
            self.rxPacket = None

        if _onlineDev != None:
            self.OnlineDevice = _onlineDev.Clone()
        else:
            self.OnlineDevice = None
            
        self.CommunicationResult = _CommunicationResult
        self.packetType = _packetType
        self.stepRx = _stepRx


class FrameSentEventArgs:
    def __init__(self, _txPacket, _onlineDev):
        self.txPacket = _txPacket.Clone()
        
        if _onlineDev != None:
            self.OnlineDevice = _onlineDev.Clone()
        else:
            self.OnlineDevice = None


class HartMaster:    
    def __init__(self, port, masterType = None, num_retry = None, retriesOnPolling = None, autoPrintTransactions = None, whereToPrint = None, logFile = None, timeout = None):
        
        if (timeout == None):
            self.TIME_OUT = 3
        else:
            self.TIME_OUT = timeout
            
        self.RECV_TIMEOUT = 0.305
        self.BYTE_TIME = 0.00916666667 # time in milliseconds to transmit a byte with HART fsk baudrate (1200)

        if (num_retry == None):
            self.RETRY_COUNT = 3
        else:
            self.RETRY_COUNT = num_retry
            
        self._numberOfRetries = self.RETRY_COUNT
        
        if (retriesOnPolling == None):
            self._retriesOnPolling = True
        else:
            self._retriesOnPolling = retriesOnPolling
            
        if (whereToPrint != None):
            self.whereToPrint = whereToPrint  
            sys.stdout = Logger(self.whereToPrint, logFile)      
        
        if (autoPrintTransactions == None):
            self.autoPrintTransactions = True
        else:
            self.autoPrintTransactions = autoPrintTransactions
        
        self.CommunicationResult = CommResult.NoResponse
        self.RecvPacket = None
        
        if (masterType == None):
            self.masterType = MASTER_TYPE.PRIMARY
        else:
            self.masterType = masterType

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
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.inter_byte_timeout = self.BYTE_TIME
        self._serial.rts = False
        
        self.NetworkMonitorIsAlive = None
        self.OnResponseOrTimeout = None
        self.monitorThread = None
        
        self.CommunicationResult = None
        self.SentPacket = None
        self.RecvPacket = None
        
        self.sent = False
        
        
    def Start(self):   
        self.msgPending = False
        self.NetIsInBurst = False
        self.waitForOack = False
        self.SendMsgEvt = threading.Event()
        self.serialLock = threading.Lock()
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
        
        
    def Stop(self):          
        if self.monitorThread is not None:            
            self.NetworkMonitorIsAlive.clear()
            self.monitorThread.join()
            self.monitorThread = None
        
        if self._serial is not None:
            self._serial.close()


    def PrintMsg(self, evtType, evtArgs):
        with globalPrintActivityLock:
            if (evtType == Events.OnCommDone):
                if ((evtArgs.CommunicationResult == CommResult.Ok) or (evtArgs.CommunicationResult == CommResult.ChecksumError)):                            
                    if (evtArgs.packetType == PacketType.ACK):
                        print('\n[SLAVE TO MASTER - ACK]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                            
                    elif (evtArgs.packetType == PacketType.OACK):
                        print('\n[SLAVE TO MASTER - OACK]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                        
                    elif (evtArgs.packetType == PacketType.BACK):
                        print('\n[BURST FRAME - BACK]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                            
                    elif (evtArgs.packetType == PacketType.OBACK):
                        print('\n[BURST FRAME - OBACK]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                        
                    elif (evtArgs.packetType == PacketType.STX):
                        print('\n[MASTER TO SLAVE - STX]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                        
                    elif (evtArgs.packetType == PacketType.OSTX):
                        print('-------------------------------------------------------------------------------', end = '')
                        print('\n[MASTER TO SLAVE - OSTX]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                        
                    else:
                        print('\n[UNKNOWN PACKET]')
                        evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                    
                    if (evtArgs.CommunicationResult == CommResult.ChecksumError):
                        print('- CHECKSUM ERROR - \n')
                            
                    print('')
                    
                elif (evtArgs.CommunicationResult == CommResult.FrameError):
                    print('\n[FRAME ERROR]')
                    evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                    print('')
                        
                elif (evtArgs.CommunicationResult == CommResult.NoResponse):
                    print('\n[NO RESPONSE RECEIVED]')
                    print('')
                        
                elif (evtArgs.CommunicationResult == CommResult.Sync):
                    print('\n[SYNCHRONIZING]')
                    evtArgs.rxPacket.printPkt(evtArgs.stepRx, evtArgs.OnlineDevice)
                    print('')
            
            elif (evtType == Events.OnFrameSent):
                print('-------------------------------------------------------------------------------', end = '')
                print('\n[MASTER TO SLAVE - STX]')
                evtArgs.txPacket.printPkt(STEP_RX.STEP_CHECKSUM, evtArgs.OnlineDevice)
                print('')


    def SendCommdoneEvent(self):                
        if self.autoPrintTransactions == True:
            evtArgs = CommunicationDoneEventArgs(self._rxPacket, self._commRes, self._packetType, self._decodeResponseStep, self.OnlineDevice)
            self.PrintMsg(Events.OnCommDone, evtArgs)
        
        # set variable to return in case of master sent a message
        self.CommunicationResult = self._commRes
        self.RecvPacket = self._rxPacket
            
        # Reset variables to receive a new frame
        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
        self.sent = False
        self._rxPacket = None


    def SendFramesentEvent(self, txPacket):
        if self.autoPrintTransactions == True:
            evtArgs = FrameSentEventArgs(txPacket, self.OnlineDevice)  
            self.PrintMsg(Events.OnFrameSent, evtArgs)


    def NetworkMonitor(self):
        while self.NetworkMonitorIsAlive.is_set():
            buffer = None

            with self.serialLock:
                buffer = self._serial.read(self._serial.in_waiting)

            if buffer != None:
                for i in range(len(buffer)):
                    rxByte = buffer[i]
                    
                    if (self._decodeResponseStep == STEP_RX.STEP_PREAMBLES):
                        #end time counter
                        if self.sent == True and self.autoPrintTransactions == True:
                            with globalPrintActivityLock:
                                # NB. Here the first whole byte has been received, time should be computed on first bit of the first byte.
                                #     for this I subtract 9ms from computed time before print
                                rxtime = ((time.perf_counter_ns() - self.t1_start) * 1.0e-6) - 9
                                print(f'response time: {rxtime} ms')
                                self.sent = False
                        
                        if self._rxPacket == None:
                            self._commRes = CommResult.Ok
                            self._packetType = PacketType.NONE
                            self._cnt = 0
                            self._rxPacket = HartPacket()

                        if (rxByte == HartPacket.PREAMBLE):
                            self._rxPacket.preamblesCnt += 1
                            if self._rxPacket.preamblesCnt >= 2:
                                self._decodeResponseStep = STEP_RX.STEP_DELIMITER
                        else:
                            self._rxPacket.delimiter = rxByte
                            self._commRes = CommResult.Sync
                            self._decodeResponseStep = STEP_RX.STEP_DELIMITER
                            self.SendCommdoneEvent()
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES

                    elif (self._decodeResponseStep == STEP_RX.STEP_DELIMITER):
                        if ((rxByte == HartPacket.PREAMBLE) and (self._rxPacket.preamblesCnt <= HartPacket.MAX_PREAMBLE_NUM)):
                            self._rxPacket.preamblesCnt += 1
                            
                        elif ((rxByte == HartPacket.PREAMBLE) and (self._rxPacket.preamblesCnt > HartPacket.MAX_PREAMBLE_NUM)):
                            self._rxPacket.preamblesCnt += 1
                            self._commRes = CommResult.Sync
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                            self.SendCommdoneEvent()
                                
                        elif (rxByte != HartPacket.PREAMBLE):
                            self._rxPacket.delimiter = rxByte
                            if (self._rxPacket.preamblesCnt >= HartPacket.MIN_PREAMBLE_NUM):
                                if (self._rxPacket.isTxPacket()):
                                    self._packetType = PacketType.STX
                                elif (self._rxPacket.isTxPacket() == False):
                                    if (self._rxPacket.isBurstPacket()):
                                        self._packetType = PacketType.BACK
                                    elif (self._rxPacket.isBurstPacket() == False):
                                        self._packetType = PacketType.ACK
                                    else:
                                        self._rxPacket.delimiter = rxByte
                                        self._commRes = CommResult.Sync
                                        self.SendCommdoneEvent()
                                        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                                        continue
                                else:
                                    self._rxPacket.delimiter = rxByte
                                    self._commRes = CommResult.Sync

                                    self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                                    continue

                                if (self._rxPacket.isLongAddressPacket()):
                                    self._decodeResponseStep = STEP_RX.STEP_LONG_ADDRESS
                                else:
                                    self._decodeResponseStep = STEP_RX.STEP_SHORT_ADDRESS
                            else:
                                self._commRes = CommResult.Sync
                                self.SendCommdoneEvent()
                                self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                    
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
                                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                                            continue
                                    else:
                                        if (((self._rxPacket.address[0] & 0x3F) != ((self.OnlineDevice.deviceType & 0x3F00) >> 8)) or (self._rxPacket.address[1] != ((self.OnlineDevice.deviceType & 0x00FF))) or (self._rxPacket.address[2] != self.OnlineDevice.uid[0]) or (self._rxPacket.address[3] != self.OnlineDevice.uid[1]) or (self._rxPacket.address[4] != self.OnlineDevice.uid[2])):
                                            self._commRes = CommResult.FrameError
                                            self.SendCommdoneEvent()
                                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                                            continue

                            if (self._rxPacket.getExpansionBytesCount() > 0):
                                self._decodeResponseStep = STEP_RX.STEP_EXPANSION
                            else:
                                self._decodeResponseStep = STEP_RX.STEP_COMMAND

                            self._cnt = 0
                        elif (self._cnt >= HartPacket.ADDR_SIZE):
                            self._rxPacket.command = rxByte
                            self._commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
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
                            self._commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                        else:
                            self._cnt += 1
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_COMMAND):
                        self._rxPacket.command = rxByte
                        self._decodeResponseStep = STEP_RX.STEP_DATA_LEN
                        
                    elif (self._decodeResponseStep == STEP_RX.STEP_DATA_LEN):
                        self._rxPacket.dataLen = rxByte

                        if ((self._rxPacket.isTxPacket() == False) and (rxByte < 2)):
                            self._commRes = CommResult.FrameError
                            self.SendCommdoneEvent()
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                            continue

                        if (self.OnlineDevice != None):
                            if ((self._rxPacket.command == HartPacket.LONG_COMMAND_INDICATOR) and ((self.OnlineDevice.hartRev == HART_REVISION.SIX) or (self.OnlineDevice.hartRev == HART_REVISION.SEVEN))):
                                if ((self._rxPacket.isTxPacket() == False) and (rxByte < 4)):
                                    self._commRes = CommResult.FrameError
                                    self.SendCommdoneEvent()
                                    self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                                    continue
                                else:
                                    if (rxByte < 2):
                                        self._commRes = CommResult.FrameError
                                        self.SendCommdoneEvent()
                                        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                                        continue

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
                            self._rxPacket.dataCount += 1

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
                            self._decodeResponseStep = STEP_RX.STEP_PREAMBLES
                    
                    elif (self._decodeResponseStep == STEP_RX.STEP_CHECKSUM):
                        checksum = self._rxPacket.ComputeChecksum()
                        if (checksum != rxByte):
                            self._commRes = CommResult.ChecksumError
                        else:
                            self._commRes = CommResult.Ok

                        self._rxPacket.checksum = rxByte
                            
                        if (self._packetType == PacketType.ACK):
                            if (self.OnResponseOrTimeout != None):
                                if ((self._commRes == CommResult.Ok) and (self._rxPacket.command == 0) and (self._rxPacket.resCode == 0)): # and (self._rxPacket.isLongAddressPacket() == False)
                                    self.OnlineDevice = HartDevice()
                                    self.OnlineDevice.Fill(self._rxPacket, self.masterType)
                                
                                if isInBurst(self._rxPacket.address[0]) == False:
                                    self.NetIsInBurst = False
                                else:
                                    self.NetIsInBurst = True
                                
                                self.SendCommdoneEvent()
                                self.OnResponseOrTimeout.set()
                            else:
                                self.SendCommdoneEvent()
                        else:
                            # Try to perform a minimum synchronization
                            if (self._packetType == PacketType.BACK) or (self._packetType == PacketType.OBACK):
                                self.NetIsInBurst = True
                                if self.msgPending == True:
                                    self.SendMsgEvt.set()
                            else:
                                if isInBurst(self._rxPacket.address[0]) == False:
                                    self.NetIsInBurst = False
                                else:
                                    self.NetIsInBurst = True
                                    
                                if self._packetType == PacketType.OSTX:
                                    self.waitForOack = True
                                elif self._packetType == PacketType.OACK:
                                    if self.msgPending == True:
                                        self.SendMsgEvt.set()
                                
                            self.SendCommdoneEvent()

                        self._decodeResponseStep = STEP_RX.STEP_PREAMBLES


    def SetOnlineDevice(self, device):
        self.OnlineDevice = device
        

    def CanRetry(self):
        if (self._numberOfRetries >= 0):
            if (self._numberOfRetries < self.RETRY_COUNT):
                if self.autoPrintTransactions == True:
                    with globalPrintActivityLock:
                        print('[ !!! RETRY !!! ]')
                
            self._numberOfRetries -= 1
            
            return True
        else:
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


    #
    # If wait for res is True, the SendFrm will wait for response
    # else the buffer is sent and the execution of the program continue.
    # Example you want to send a frame with a wrong checksum, you want to ewait a response
    # but if you want to send two consecutive frame with a small gap, you should not
    # want to wait a response after sending the first buffer.
    # You can omit this parameter. it is True by default.
    # In the second case probably you don't want to close rts signal after sending first frame.
    # You cna omit this parameter, default is True
    #
    def SendCustomFrame(self, txFrame, waitForRes = True, closeRTS = True):
        commRes = CommResult.NoResponse
        self._numberOfRetries = self.RETRY_COUNT
        rxPkt = None
        while ((commRes != CommResult.Ok) and self.CanRetry()):
            commRes, rxPkt = self.SendFrm(txFrame, waitForRes, closeRTS)
        
        return commRes, rxPkt
        

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
        
        
    def WaitForResponse(self):
        event_is_set = self.OnResponseOrTimeout.wait(self.TIME_OUT)

        if (event_is_set == False):
            if self.autoPrintTransactions == True:
                with globalPrintActivityLock:
                    print(f'time out: {(time.perf_counter_ns() - self.t1_start) * 1.0e-6} ms')
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()

        self.OnResponseOrTimeout.clear()

 
    def SendCmd(self, command, Data, DataLen, UseBroadcastAddress):
        txPacket = None
        if (self.OnlineDevice != None):
            txPacket = HartPacket()
            
            txPacket.PrepareTxPacket(self.OnlineDevice, self.masterType, False, self.OnlineDevice.pollAddr, Data, DataLen, command, UseBroadcastAddress)
            txFrame = txPacket.ToFrame()
            
            self.WriteOnSerial(txFrame, len(txFrame))
            self.SendFramesentEvent(txPacket)

            self.WaitForResponse()
        else:
            self._commRes = CommResult.NoResponse
            self.SendCommdoneEvent()
   
        return self.CommunicationResult, txPacket, self.RecvPacket


    def SendFrm(self, txFrame, waitForRes = True, closeRTS = True):
        if (txFrame is not None) and (len(txFrame) > 0):
            self.WriteOnSerial(txFrame, len(txFrame), closeRTS)

            self._numberOfRetries = -1
            if self.autoPrintTransactions == True:
                with globalPrintActivityLock:
                    print('-------------------------------------------------------------------------------', end = '')
                    print('\n[MASTER TO SLAVE - STX] - {0}'.format(datetime.now(tz=None)))
                    print('Sent bytes: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(txFrame[0:len(txFrame)])))
                    print('\n')

            if waitForRes == True:
                self.WaitForResponse()
            
            return self.CommunicationResult, self.RecvPacket
        else:
            if self.autoPrintTransactions == True:
                with globalPrintActivityLock:
                    print('-------------------------------------------------------------------------------', end = '')
                    print('\n[MASTER TO SLAVE - STX] - {0}'.format(datetime.now(tz=None)))
                    print('Frame to send is None or Empty\n\n')
            
            return CommResult.NoResponse, None


    def SendShortCommandZero(self, pollAddr):
        txPacket = HartPacket()
        txPacket.PrepareTxPacket(None, self.masterType, True, pollAddr, None, 0, 0, False)
        txFrame = txPacket.ToFrame()
        
        self.WriteOnSerial(txFrame, len(txFrame))
        self.SendFramesentEvent(txPacket)
        
        self.WaitForResponse()

        if self.CommunicationResult != CommResult.Ok:
            return self.CommunicationResult, txPacket, self.RecvPacket, None
        else:
            return self.CommunicationResult, txPacket, self.RecvPacket, self.OnlineDevice


    def WriteOnSerial(self, buffer, len, closeRTS = True):
        self.SendMsgEvt.clear()
        
        if self.NetIsInBurst == True:
            self.msgPending = True
            self.SendMsgEvt.wait(3)
            
        if self.waitForOack == True:
            self.msgPending = True
            self.SendMsgEvt.wait(1)
            self.waitForOack = False

        with self.serialLock:
            self._serial.rts = True
            self._serial.write(buffer)
            
            # wait for all byte go out before to close RTS.
            # wait for two additional byte to avoid problems...
            time.sleep(self.BYTE_TIME * (len + 2))

            if closeRTS == True:
                self._serial.rts = False

        #start time counter
        self.t1_start = time.perf_counter_ns()
        self.sent = True



