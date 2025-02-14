###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
import struct
from PyHART.HARTcore.PyHARTengine.Utils import *
from PyHART.HARTcore.PyHARTengine.Common import *


class HartPacket:
    ADDR_SIZE = 5
    EXT_SIZE = 3
    DATA_SIZE = 256
    MAX_PREAMBLE_NUM = 20
    MIN_PREAMBLE_NUM = 2
    PREAMBLE = 255
    LONG_COMMAND_INDICATOR = 31

    def __init__(self):
        self.preamblesCnt = 0
        self.delimiter = 0
        self.address = bytearray(HartPacket.ADDR_SIZE)
        self.expansionBytes = bytearray(HartPacket.EXT_SIZE)
        self.command = 0
        self.dataLen = 0
        self.resCode = 0
        self.devStatus = 0
        self.data = bytearray(HartPacket.DATA_SIZE)
        self.dataCount = 0
        self.checksum = 0
        
    def GetLongCommand(self, command, data):
        if ((command == HartPacket.LONG_COMMAND_INDICATOR) and (len(data) >= 2)):
            cmdByte = bytearray(2)
            return (struct.unpack_from('>H', data, 0))[0]
            
        return 0x0000
        
    def isLongAddressPacket(self):
        if ((self.delimiter & 0x80) == 0x80):
            return True
        else:
            return False
        
    def getExpansionBytesCount(self):
        return ((self.delimiter & 0x60) >> 5)
        
    def isTxPacket(self):
        if (((self.delimiter & 0x07) == 0x06) or ((self.delimiter & 0x07) == 0x01)):
            return False
        elif (self.delimiter & 0x07) == 0x02:
            return True
        else:
            return None
        
    def isBurstPacket(self):
        if ((self.delimiter & 0x07) == 0x01):
            return True
        elif ((self.delimiter & 0x07) != 0x01):
            return False
        else:
            return None            
        
    def ComputeChecksum(self):
        checksum = self.delimiter
        
        if (self.isLongAddressPacket()):
            for idx in range(HartPacket.ADDR_SIZE):
                checksum ^= self.address[idx]
        else:
            checksum ^= self.address[0]
            
        expBytesCnt = self.getExpansionBytesCount();
        for idx in range(expBytesCnt):
            checksum ^= self.expansionBytes[idx];
        
        checksum ^= self.command
            
        checksum ^= self.dataLen

        maxLen = 0
        if (self.isTxPacket() == False):
            checksum ^= self.resCode
            checksum ^= self.devStatus
            maxLen = self.dataLen - 2
        else:
            maxLen = self.dataLen

        for idx in range(maxLen):
            checksum ^= self.data[idx]

        return checksum
        
    def ToFrame(self):
        txFrame = bytearray()
        
        for pos in range(self.preamblesCnt):
            txFrame.append(HartPacket.PREAMBLE)
            
        txFrame.append(self.delimiter)
        
        if (self.isLongAddressPacket()):
            txFrame.extend(self.address)
        else:
            txFrame.append(self.address[0])
            
        expBytes = self.getExpansionBytesCount()
        for pos in range(expBytes):
            txFrame.append(self.expansionBytes[pos])
        
        if (self.command > 255):
            txFrame.append(HartPacket.LONG_COMMAND_INDICATOR)
        else:
            txFrame.append(self.command)

        txFrame.append(self.dataLen)
        
        len = 0
        if (self.isTxPacket() == False):
            txFrame.append(self.resCode)
            txFrame.append(self.devStatus)
            len = self.dataLen - 2
        else:
            len = self.dataLen
        
        for pos in range(len):
            txFrame.append(self.data[pos])

        txFrame.append(self.checksum)

        return txFrame

        
    def Clone(self):
        retPacket = HartPacket()

        retPacket.preamblesCnt = self.preamblesCnt
        retPacket.delimiter = self.delimiter
        retPacket.address = self.address[:]
        retPacket.command = self.command
        retPacket.expansionBytes = self.expansionBytes[:]
        retPacket.dataLen = self.dataLen # lenght of all data bytes, data+rescodes+longcommand
        retPacket.resCode = self.resCode
        retPacket.devStatus = self.devStatus
        retPacket.data = self.data[:]
        retPacket.dataCount = self.dataCount # lenght only of the data bytes
        retPacket.checksum = self.checksum

        return retPacket
        
    def PrepareTxPacket(self, OnlineDevice, MasterType, isShortAddr, pollAddr, txData, txDataLen, _command, UseBroadcastAddress):
        if (OnlineDevice == None):
            self.preamblesCnt = HartPacket.MAX_PREAMBLE_NUM
        else:
            self.preamblesCnt = OnlineDevice.reqPreambles
            
        if (isShortAddr == True):
            self.delimiter = 2

            if (MasterType == MASTER_TYPE.PRIMARY):
                self.address[0] = (0x80 | pollAddr)
            else:
                self.address[0] = pollAddr
        else:
            self.delimiter = 130
            if (OnlineDevice != None): 
                if (UseBroadcastAddress == False):
                    self.address = OnlineDevice.longAddress[:]
                else:
                    self.address[0] = (OnlineDevice.longAddress[0] & 0xC0)
                    self.address[1] = 0
                    self.address[2] = 0
                    self.address[3] = 0
                    self.address[4] = 0            
        
        if ((_command > 255) and (OnlineDevice != None) and ((OnlineDevice.hartRev == HART_REVISION.SIX) or (OnlineDevice.hartRev == HART_REVISION.SEVEN))):
            self.command = HartPacket.LONG_COMMAND_INDICATOR
            self.dataLen = 2
            if ((txDataLen > 0) and (txData != None)):
                for idx in range(txDataLen):
                    self.data[idx + 2] = txData[idx]

            cmdBytes = struct.pack('>H', _command)
            self.data[0] = cmdBytes[0]
            self.data[1] = cmdBytes[1]
            self.dataLen += txDataLen
        else:
            if ((txDataLen > 0) and (txData != None)):
                for idx in range(txDataLen):
                    self.data[idx] = txData[idx]

            self.dataLen = txDataLen
            if (_command <= 255):
                self.command = _command
            else:
                cmdBytes = struct.pack('>H', _command)
                self.command = cmdBytes[1]
        
        self.checksum = self.ComputeChecksum()
    

    def FillFromTxFrame(self, txFrame):
        idx = 0

        self.preamblesCnt = 0
        while (txFrame[idx] == HartPacket.PREAMBLE):
            self.preamblesCnt += 1
            idx += 1

        self.delimiter = txFrame[idx]
        idx += 1
        
        if (self.isLongAddressPacket()):
            self.address[0] = txFrame[idx]
            idx += 1
            self.address[1] = txFrame[idx]
            idx += 1
            self.address[2] = txFrame[idx]
            idx += 1
            self.address[3] = txFrame[idx]
            idx += 1
            self.address[4] = txFrame[idx]
            idx += 1
        else:
            self.address[0] = txFrame[idx]
            idx += 1

        expBytes = self.getExpansionBytesCount()
        for pos in range(expBytes):
            self.expansionBytes[pos] = txFrame[idx]
            idx += 1

        self.command = txFrame[idx]
        idx += 1
        self.dataLen = txFrame[idx]
        idx += 1

        for pos in range(self.dataLen):
            self.data[pos] = txFrame[idx]
            idx += 1

        self.checksum = txFrame[idx]

    def printPkt(self, step, OnlineDevice):
        if (step >= STEP_RX.STEP_PREAMBLES):
            print('Preambles Count: {0:d}'.format(self.preamblesCnt))
            
        if (step >= STEP_RX.STEP_DELIMITER):
            print('      Delimiter: 0x{0:02X}'.format(self.delimiter))
            
        if ((step >= STEP_RX.STEP_SHORT_ADDRESS) or (step >= STEP_RX.STEP_LONG_ADDRESS)):
            if (self.isLongAddressPacket()):
                print ('        Address: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.address[0:HartPacket.ADDR_SIZE])))
            else:
                print('        Address: 0x{0:02X}'.format(self.address[0]))
        
        if (step >= STEP_RX.STEP_EXPANSION):
            expansionCnt = self.getExpansionBytesCount()
            if (expansionCnt > 0):
                print ('      Expansion: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.expansionBytes[0:expansionCnt])))
            
        if (step >= STEP_RX.STEP_COMMAND):
            print('        Command: {0:d}'.format(self.command))
            
        if (step >= STEP_RX.STEP_DATA_LEN):
            print('    Data Length: {0:d}'.format(self.dataLen))
            
        if (self.isTxPacket() == False):
            if (step >= STEP_RX.STEP_RESPONSE_CODE):
                if (self.resCode == 0):
                    print('  Response Code: {0:d}'.format(self.resCode))
                else:
                    print('  Response Code: {0:d}'.format(self.resCode) + ' - NOT OK -');

                errors = hasCommunicationErrors(self.resCode)
                l = len(errors)
                for idx in range(l):
                    print('                 ' + errors[idx])

            if (step >= STEP_RX.STEP_DEVICE_STATUS):
                print('  Device Status: 0x{0:02X}'.format(self.devStatus))
                LastDevStatus = GetDevStatusDesc(self.devStatus)
                l = len(LastDevStatus)
                for idx in range (l):
                    print('                 ' + LastDevStatus[idx])            
        
        if ((step >= STEP_RX.STEP_DATA) and (self.dataLen > 0)):
            startIdx = 0
            longCmd = 0x0000
            
            if ((OnlineDevice != None) and ((OnlineDevice.hartRev == HART_REVISION.SIX) or (OnlineDevice.hartRev == HART_REVISION.SEVEN))):
                if (self.command == HartPacket.LONG_COMMAND_INDICATOR):
                    if (self.isTxPacket() == False):
                        startIdx = 2
                        longCmd = self.GetLongCommand(self.command, self.data)
                        print('   Long Command: {0:d} - 0x{1:02X} 0x{2:02X}'.format(longCmd, self.data[0], self.data[1]))
                        
                        print('           Data: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.data[startIdx:self.dataCount])))
                    else:
                        startIdx = 2
                        longCmd = self.GetLongCommand(self.command, self.data)
                        print('   Long Command: {0:d} - 0x{1:02X} 0x{2:02X}'.format(longCmd, self.data[0], self.data[1]))
                        
                        if ((self.dataLen - 2) > 0):
                            print('           Data: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.data[startIdx:self.dataLen])))
                else:
                    if (self.isTxPacket() == False):                            
                        print('           Data: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.data[startIdx:(self.dataCount)])))
                    else:
                        print('           Data: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.data[startIdx:self.dataLen])))
            else:
                if (self.isTxPacket() == False):                    
                    print('           Data: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.data[startIdx:(self.dataCount)])))
                else:
                    print('           Data: ' + ' '.join('0x{0:02X}'.format(val) for i, val in enumerate(self.data[startIdx:self.dataLen])))
        
        if (step >= STEP_RX.STEP_CHECKSUM):
            print('       Checksum: 0x{0:02X}'.format(self.checksum))
        
        if ((step >= STEP_RX.STEP_SHORT_ADDRESS) or (step >= STEP_RX.STEP_LONG_ADDRESS)):
            if (isInBurst(self.address[0])):
                print ('- BURST ON -')

