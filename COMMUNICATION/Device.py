###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
from enum import IntEnum
import CommCore
import Comm
import struct
import Utils
import Packet

class HART_REVISION(IntEnum):
    FIVE = 5
    SIX = 6
    SEVEN = 7

UID_SIZE = 3

class HartDevice():
    def __init__(self):
        self.manufacturerId = 0
        self.deviceType = 0
        self.deviceRevision = 0
        self.reqPreambles = 0
        self.uid = bytearray(UID_SIZE)
        self.pollAddr = 0
        self.longAddress = bytearray(Packet.ADDR_SIZE)
        self.hartRev = HART_REVISION.SEVEN
        self.isInBurst = False
        self.deviceProfile = 0
        self.flags = 0
        self.numOfVar = 0
        self.ExtendedFieldDevStatus = 0
        self.HardwareRevisionLevelPhysicalSignalingCode = 0
        self.SwRevisionLevel = 0
    
    def manufacturerIdStr(self):
        return '0x{0:04X}'.format(self.manufacturerId)
        
    def DeviceTypeStr(self):
        return '0x{0:04X}'.format(self.deviceType)
        
    def DeviceRevisionStr(self):
        return '0x{0:02X}'.format(self.deviceRevision)
        
    def ReqPreamblesStr(self):
        return '{0:d}'.format(self.reqPreambles)
        
    def UidStr(self):
        return '0x{0:02X}, 0x{1:02X}, 0x{2:02X}'.format(self.uid[0], self.uid[1], self.uid[2])
        
    def PollAddrStr(self):
        return '0x{0:02X}'.format(self.pollAddr)
        
    def LongAddressStr(self):
        return '0x{0:02X}, 0x{1:02X}, 0x{2:02X}, 0x{3:02X}, 0x{4:02X}'.format(self.longAddress[0], self.longAddress[1], self.longAddress[2], self.longAddress[3], self.longAddress[4])
        
    def HartRevStr(self):
        return '{0:d}'.format(self.hartRev)
        
    def ProfileStr(self):
        return Utils.GetProfileString(self.deviceProfile)
        
    def DeviceFlagsStr(self):
        allflags = Utils.GetDevFlags(self.flags)
        flagsStr = ""
        for idx in range(len(allflags)):
            flagsStr += allflags[idx]
            if (idx < (len(allflags) - 1)):
               flagsStr += ", " 
        return flagsStr
        
    def ExtendedFieldDevStatusStr(self):
        allStat = Utils.GetExtendedFieldDeviceStatus(self.ExtendedFieldDevStatus)
        str = ""
        if (len(allStat) > 0):
            for idx in range(len(allStat)):
                str += allStat[idx]
                if (idx < (len(allStat) - 1)):
                   str += ", "
        else:
            str = '0x{0:02X}'.format(self.ExtendedFieldDevStatus)
        return str 

    def PhysicalSignalingCodeStr(self):
        return  Utils.GetSignalString(self.HardwareRevisionLevelPhysicalSignalingCode)
        
    def HardwareRevisionLevelStr(self):
        return '{0:d}'.format(Utils.GetHardwareRevisionLevel(self.HardwareRevisionLevelPhysicalSignalingCode))
    
    def SwRevisionLevelStr(self):
        return '{0:d}'.format(self.SwRevisionLevel)
    
    def NumOfVarStr(self):
        return '{0:d}'.format(self.numOfVar)
        
    def Clone(self):
        dev = HartDevice()
        dev.manufacturerId = self.manufacturerId
        dev.deviceType = self.deviceType
        dev.deviceRevision = self.deviceRevision
        dev.reqPreambles = self.reqPreambles
        dev.pollAddr = self.pollAddr
        dev.hartRev = self.hartRev
        dev.isInBurst = self.isInBurst
        dev.uid = self.uid[:]
        dev.longAddress = self.longAddress[:]
        dev.deviceProfile = self.deviceProfile
        dev.flags = self.flags
        dev.ExtendedFieldDevStatus = self.ExtendedFieldDevStatus
        dev.numOfVar = self.numOfVar
        dev.HardwareRevisionLevelPhysicalSignalingCode = self.HardwareRevisionLevelPhysicalSignalingCode
        return dev
        
    def SetLongAddress(self, MasterType):
        if (self.hartRev == HART_REVISION.SEVEN):
            if (MasterType == CommCore.MASTER_TYPE.PRIMARY):
                self.longAddress[0] = ((0x3F00 & self.deviceType) >> 8)
                self.longAddress[0] |= 0x80
                self.longAddress[1] = (self.deviceType & 0x00FF)
            else:
                self.longAddress[0] = ((0x3F00 & self.deviceType) >> 8)
                self.longAddress[1] = (self.deviceType & 0x00FF)
        else:
            if (MasterType == CommCore.MASTER_TYPE.PRIMARY):
                self.longAddress[0] = ((0x3F & self.manufacturerId) | 0x80)
                self.longAddress[1] = self.deviceType
            else:
                self.longAddress[0] = (0x3F & self.manufacturerId)
                self.longAddress[1] = self.deviceType

        self.longAddress[2] = self.uid[0]
        self.longAddress[3] = self.uid[1]
        self.longAddress[4] = self.uid[2]
        
    def Fill(self, rxPacket, MasterType):
        if (rxPacket.data[4] == 5):
            self.hartRev = HART_REVISION.FIVE
        elif (rxPacket.data[4] == 6):
            self.hartRev = HART_REVISION.SIX
        elif (rxPacket.data[4] == 7):
            self.hartRev = HART_REVISION.SEVEN
            
        if ((self.hartRev == HART_REVISION.FIVE) or (self.hartRev == HART_REVISION.SIX)):
            self.deviceType = rxPacket.data[2]
            self.manufacturerId = rxPacket.data[1]
        elif (self.hartRev == HART_REVISION.SEVEN):
            self.deviceType = (struct.unpack_from(">H", rxPacket.data, 1))[0]
            self.manufacturerId = (struct.unpack_from(">H", rxPacket.data, 17))[0]
            
        self.pollAddr = rxPacket.address[0] & 0x3F
            
        self.deviceRevision = rxPacket.data[5]
        self.uid[0] = rxPacket.data[9]
        self.uid[1] = rxPacket.data[10]
        self.uid[2] = rxPacket.data[11]
        self.reqPreambles = rxPacket.data[3]
        self.SetLongAddress(MasterType)
        
        if (Utils.isInBurst(rxPacket.address[0])):
            self.isInBurst = True
        else:
            self.isInBurst = False
            
        self.flags = rxPacket.data[8]
        self.HardwareRevisionLevelPhysicalSignalingCode = rxPacket.data[7]
        self.SwRevisionLevel = rxPacket.data[6]
        
        if ((self.hartRev == HART_REVISION.SIX) or (self.hartRev == HART_REVISION.SEVEN)):
            self.deviceProfile = rxPacket.data[21]
            self.ExtendedFieldDevStatus = rxPacket.data[16]
            self.numOfVar = rxPacket.data[13]

    def printDev(self):
        print("       Manufacturer ID: " + self.manufacturerIdStr())
        print("           Device Type: " + self.DeviceTypeStr())
        print("       Device Revision: " + self.DeviceRevisionStr()) 
        print("     Request Preambles: " + self.ReqPreamblesStr()) 
        print("                   UID: " + self.UidStr())
        print("       Polling Address: " + self.PollAddrStr()) 
        print("          Long Address: " + self.LongAddressStr())
        print("         HART Revision: " + self.HartRevStr())
        print("                 Flags: " + self.DeviceFlagsStr())
        print(" SoftwareRevisionLevel: " + self.SwRevisionLevelStr())
        print(" HardwareRevisionLevel: " + self.HardwareRevisionLevelStr())
        print(" PhysicalSignalingCode: " + self.PhysicalSignalingCodeStr())
        if ((self.hartRev == HART_REVISION.SIX) or (self.hartRev == HART_REVISION.SEVEN)):
            print("      Num of Variables: " + self.NumOfVarStr())
            print("               Profile: " + self.ProfileStr())
            print("ExtendedFieldDevStatus: " + self.ExtendedFieldDevStatusStr())
        



















