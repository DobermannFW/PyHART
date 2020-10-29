###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
import sys
import CommCore
import Packet
import Device
import threading
import queue
import Utils
from datetime import datetime
import time
from enum import IntEnum

class WhereToPrint(IntEnum):
    BOTH = 0
    TERMINAL = 1
    FILE = 2

class Logger():
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
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

class HartMaster():
    def __init__(self, _port, masterType = None, num_retry = None, retriesOnPolling = None, autoPrintTransactions = None, whereToPrint = None, logFile = None, rt_os = None, manageRtsCts = None):    
        
        self.hart = CommCore.HartComm(_port, masterType, rt_os, manageRtsCts)
        self.EventHandlerIsAlive = None
        self.EventHandlerThread = None
        self.CommDone = None
        
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
        
        self.CommunicationResult = CommCore.CommResult.NoResponse
        self.RecvPacket = None
        self.SentPacket = None
        
        self.sock = None
        
        if (self.autoPrintTransactions == True):
            print("\n")
            print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print("::::::                            PyHART                                 ::::::")
            print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print("\n")
            
    def Start(self):    
        self.CommDone = threading.Event()
        self.CommDone.set()
        
        self.EventHandlerIsAlive = threading.Event()
        
        self.EventHandlerThread = threading.Thread(target = self.EventHandler)
        self.EventHandlerThread.daemon = True
        
        self.EventHandlerIsAlive.set()
        
        self.EventHandlerThread.start()
        
        self.hart.Open()
        
    def Stop(self):
        self.hart.Close()
        if (self.EventHandlerIsAlive is not None):
            self.EventHandlerIsAlive.clear()  
        
        if self.EventHandlerThread is not None:
            self.EventHandlerThread.join()
            self.EventHandlerThread = None  
            self.EventHandlerIsAlive = None   
            
    def EventHandler(self):
        while (self.EventHandlerIsAlive is not None) and (self.EventHandlerIsAlive.is_set()):
            event = None
            if (self.hart.EvtQueue.empty() == False):
                event = self.hart.EvtQueue.get()
                if (event != None):
                    evtType = event[0]
                    evtArgs = event[1]
                    
                if (evtType == CommCore.Events.OnCommDone):
                    if ((evtArgs.CommunicationResult == CommCore.CommResult.Ok) or (evtArgs.CommunicationResult == CommCore.CommResult.ChecksumError)):                            
                        if (evtArgs.packetType == CommCore.PacketType.ACK):
                            if (self.autoPrintTransactions == True):
                                print("-------------------------------------------------------------------------------")
                                print("[SLAVE TO MASTER - ACK] - {0}".format(evtArgs.currtime))
                                evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            
                            if (self.CommDone.is_set() == False):
                                self.CommunicationResult = evtArgs.CommunicationResult
                                self.RecvPacket = evtArgs.rxPacket 
                                self.CommDone.set()
                                
                        elif (evtArgs.packetType == CommCore.PacketType.OACK):
                            if (self.autoPrintTransactions == True):
                                print("-------------------------------------------------------------------------------")
                                print("[SLAVE TO MASTER - OACK] - {0}".format(evtArgs.currtime))
                                evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            
                        elif (evtArgs.packetType == CommCore.PacketType.BACK):
                            if (self.autoPrintTransactions == True):
                                print("-------------------------------------------------------------------------------")
                                print("[BURST FRAME - BACK] - {0}".format(evtArgs.currtime))
                                evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            
                        elif (evtArgs.packetType == CommCore.PacketType.STX):
                            if (self.autoPrintTransactions == True):
                                print("-------------------------------------------------------------------------------")
                                print("[MASTER TO SLAVE - STX] - {0}".format(evtArgs.currtime))
                                evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            
                        elif (evtArgs.packetType == CommCore.PacketType.OSTX):
                            if (self.autoPrintTransactions == True):
                                print("-------------------------------------------------------------------------------")
                                print("[MASTER TO SLAVE - OSTX] - {0}".format(evtArgs.currtime))
                                evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            
                        else:
                            if (self.autoPrintTransactions == True):
                                print("-------------------------------------------------------------------------------")
                                print("[UNKNOWN PACKET] - {0}".format(evtArgs.currtime))
                                evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                        
                        if (evtArgs.CommunicationResult == CommCore.CommResult.ChecksumError):
                            if (self.autoPrintTransactions == True):
                                print ("- CHECKSUM ERROR -")
                                
                        if (self.autoPrintTransactions == True):
                            print("\n")
                        
                    elif (evtArgs.CommunicationResult == CommCore.CommResult.FrameError):
                        if (self.autoPrintTransactions == True):
                            print("-------------------------------------------------------------------------------")
                            print("[FRAME ERROR] - {0}".format(evtArgs.currtime))
                            evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            print("\n")
                            
                    elif (evtArgs.CommunicationResult == CommCore.CommResult.NoResponse):
                        if (self.autoPrintTransactions == True):
                            print("-------------------------------------------------------------------------------")
                            print("[NO RESPONSE RECEIVED] - {0}".format(evtArgs.currtime))
                            print("\n")
                        
                        if (self.CommDone.is_set() == False):
                            self.CommunicationResult = evtArgs.CommunicationResult
                            self.CommDone.set()
                            
                    elif (evtArgs.CommunicationResult == CommCore.CommResult.Sync):
                        if (self.autoPrintTransactions == True):
                            print("-------------------------------------------------------------------------------")
                            print("[SYNCHRONIZING ON PREAMBLES] - {0}".format(evtArgs.currtime))
                            evtArgs.rxPacket.printPkt(evtArgs.stepRx, self.OnlineDevice())
                            print("\n")
                
                elif (evtType == CommCore.Events.OnFrameSent):
                    if (self.autoPrintTransactions == True):
                        print("-------------------------------------------------------------------------------")
                        print("[MASTER TO SLAVE - STX] - {0}".format(evtArgs.currtime))
                        evtArgs.txPacket.printPkt(CommCore.STEP_RX.STEP_CHECKSUM, self.OnlineDevice())
                        print("\n")
                        
                    self.SentPacket = evtArgs.txPacket
                    
            time.sleep(0.250) # Do not overload the machine especially for embedded systems (eg. Raspberry Pi). Let time to CommCore listener thread
    
    def PerformTransaction(self, commandNumber, txData):
        self._numberOfRetries = self.RETRY_COUNT
        self.CommunicationResult = CommCore.CommResult.NoResponse
        
        while ((self.CommunicationResult == CommCore.CommResult.NoResponse) and (self.ShouldRetry())):
            self.CommDone.clear()
            if (txData is not None):
                self.hart.SendCommand(commandNumber, txData, len(txData))
            else:
                self.hart.SendCommand(commandNumber, txData, 0)
            self.CommDone.wait()
        
        return self.CommunicationResult, self.SentPacket, self.RecvPacket
        
    def PerformBroadcastTransaction(self, commandNumber, txData):
        self._numberOfRetries = self.RETRY_COUNT
        self.CommunicationResult = CommCore.CommResult.NoResponse
        
        while ((self.CommunicationResult == CommCore.CommResult.NoResponse) and (self.ShouldRetry())):
            self.CommDone.clear()
            if (txData is not None):
                self.hart.SendBroadcastCommand(commandNumber, txData, len(txData))
            else:
                self.hart.SendBroadcastCommand(commandNumber, txData, 0)
            self.CommDone.wait()
        
        return self.CommunicationResult, self.SentPacket, self.RecvPacket
        
    def SendCustomFrame(self, txFrame):
        self._numberOfRetries = self.RETRY_COUNT
        self.CommunicationResult = CommCore.CommResult.NoResponse
        
        while ((self.CommunicationResult == CommCore.CommResult.NoResponse) and (self.ShouldRetry())):
            self.CommDone.clear()
            self.hart.SendFrame(txFrame)
            self.CommDone.wait()
            
        return self.CommunicationResult, self.SentPacket, self.RecvPacket

    def LetKnowDevice(self, pollAddr):
        if (self._retriesOnPolling == False):
            self.CommDone.clear()
            self.hart.ReadUniqeId(pollAddr)
            self.CommDone.wait()
        else:
            self._numberOfRetries = self.RETRY_COUNT
            self.CommunicationResult = CommCore.CommResult.NoResponse
            
            while ((self.CommunicationResult == CommCore.CommResult.NoResponse) and (self.ShouldRetry())):
                self.CommDone.clear()
                self.hart.ReadUniqeId(pollAddr)
                self.CommDone.wait()
        
        return self.CommunicationResult, self.SentPacket, self.RecvPacket, self.OnlineDevice()
        
    def OnlineDevice(self):
        return self.hart.OnlineDevice
        
    def SetOnlineDevice(self, device):
        self.hart.OnlineDevice = device

    def ShouldRetry(self):
        if (self._numberOfRetries >= 0):
            if (self._numberOfRetries < self.RETRY_COUNT):  
                if (self.autoPrintTransactions == True):
                    print("-------------------------------------------------------------------------------")
                    print("RETRY {0}\n".format(self.RETRY_COUNT - self._numberOfRetries))
            
            self._numberOfRetries -= 1
            return True
        else:
            return False
