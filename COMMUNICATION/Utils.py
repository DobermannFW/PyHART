###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
from serial.tools import list_ports
from PyHART.COMMUNICATION.Common import *


"""
-------------------------------------------------------------------------------
GET PY_HART REVISION
-------------------------------------------------------------------------------
"""
# MAJOR HART PROTOCOL REVISION
# PyHART MAJOR REVISION
# PyHART MINOR REVISION
def PyHART_Revision():
    return "7.2.2"


"""
-------------------------------------------------------------------------------
BURST
-------------------------------------------------------------------------------
"""
#
# Indicates if a device is in burst or no by passing first byte of the address
# when you execute an hart command.
#
def isInBurst(address0):
    if ((address0 & 0x40) > 0):
        return True
    else:
        return False

"""
-------------------------------------------------------------------------------
COM PORTS
-------------------------------------------------------------------------------
"""
#
# ATTENTION: In revisions till the current, this function has been tested only under Windows OS
# This functions enumerates all available COM ports and add a incremental number before each port.
# This is useful if you want to create a menu.
# in addition it is possible if to add a "Quit" choose at the end of the list, for example
# if the user wants to leave the application.
# This function returns the list of the ports and the count of found com ports.
#
def ListCOMPort(addQuitOption):
    print("\nAvailable COM ports")
    i = 1
    listOfComPorts = list_ports.comports()
    for portsInfo in enumerate(listOfComPorts):
        print("  {0}: ".format(i) + "{0} - {1}".format(portsInfo[1].device, portsInfo[1].description))
        i += 1

    if (addQuitOption == True):
        print("  {0}: ".format(i) + "Quit")

    return (i - 1), listOfComPorts

#
# This function is used combined with "ListCOMPort".
# You can pass the user selection (of the incremental number) and the list of ports
# returned from ListCOMPort.
# This function returns the name of the port, for example "COM1" or none if the selection is not valid.
#    
def GetCOMPort(sel, listOfComPorts):
    try:
        if (listOfComPorts is not None) and (sel > 0):
            i = 1
            for portsInfo in enumerate(listOfComPorts):
                if (i == sel):
                    return "{0}".format(portsInfo[1].device)
                i += 1
    except:
        return None
        
    return None

"""
-------------------------------------------------------------------------------
MEASURAMENT UNITS
-------------------------------------------------------------------------------
"""

#
# class to hanlde a single unit: [code + name]
#
class HART_UNIT():
    def __init__(self, _untcode = 251, _name = "None"):
        self.untcode = _untcode
        self.name = _name

#
# array of HART_UNIT containing all HART measurament units
#
ALL_HART_UNITS = [
    HART_UNIT(1, "Inches H2O 68F"),
    HART_UNIT(2, "Inches HG 0C"),
    HART_UNIT(3, "Feet H2O 68F"),
    HART_UNIT(4, "Millimiter H2O 68F"),
    HART_UNIT(5, "Millimiter HG"),
    HART_UNIT(6, "Psi"),
    HART_UNIT(7, "Bar"),
    HART_UNIT(8, "Millibar"),
    HART_UNIT(9, "Gram per Centimeter^2"),
    HART_UNIT(10, "Kilogram per Centimeter^2"),
    HART_UNIT(11, "Pascal"),
    HART_UNIT(12, "Kilopascal"),
    HART_UNIT(13, "Torr"),
    HART_UNIT(14, "Atmosphere"),
    HART_UNIT(15, "Cubic Feet per Minute"),
    HART_UNIT(16, "Gallons per Minute"),
    HART_UNIT(17, "Liters per Minute"),
    HART_UNIT(18, "Imperial Gallons per Minute"),
    HART_UNIT(19, "Cubic Meter per Hour"),
    HART_UNIT(20, "Feet per Second"),
    HART_UNIT(21, "Meter per Second"),
    HART_UNIT(22, "Gallons per Second"),
    HART_UNIT(23, "Million Gallons per Day"),
    HART_UNIT(24, "Liters per Second"),
    HART_UNIT(25, "Million Liters per Day"),
    HART_UNIT(26, "Cubic Feet per Second"),
    HART_UNIT(27, "Cubic Feet per Day"),
    HART_UNIT(28, "Cubic Meter per Second"),
    HART_UNIT(29, "Cubic Meter per Day"),
    HART_UNIT(30, "Imperial Gallons per Hour"),
    HART_UNIT(31, "Imperial Gallons per Day"),
    HART_UNIT(32, "Celsius"),
    HART_UNIT(33, "Fahrenheit"),
    HART_UNIT(34, "Rankine"),
    HART_UNIT(35, "Kelvin"),
    HART_UNIT(36, "Millivolts"),
    HART_UNIT(37, "Ohms"),
    HART_UNIT(38, "Hertz"),
    HART_UNIT(39, "Milliampere"),
    HART_UNIT(40, "Gallons"),
    HART_UNIT(41, "Liters"),
    HART_UNIT(42, "Imperial Gallons"),
    HART_UNIT(43, "Cubic Meters"),
    HART_UNIT(44, "Feet"),
    HART_UNIT(45, "Meter"),
    HART_UNIT(46, "Barrels"),
    HART_UNIT(47, "Inch"),
    HART_UNIT(48, "Centimeter"),
    HART_UNIT(49, "Millimeter"),
    HART_UNIT(50, "Minutes"),
    HART_UNIT(51, "Seconds"),
    HART_UNIT(52, "Hours"),
    HART_UNIT(53, "Day"),
    HART_UNIT(54, "Centistokes"),
    HART_UNIT(55, "Centipoise"),
    HART_UNIT(56, "Microsiemens"),
    HART_UNIT(57, "Percent"),
    HART_UNIT(58, "Volts"),
    HART_UNIT(59, "Ph"),
    HART_UNIT(60, "Grams"),
    HART_UNIT(61, "Kilograms"),
    HART_UNIT(62, "Metric Tons"),
    HART_UNIT(63, "Pounds"),
    HART_UNIT(64, "Short Tons"),
    HART_UNIT(65, "Long Tons"),
    HART_UNIT(66, "Millisiemens per centimeter"),
    HART_UNIT(67, "Microsiemens per centimeter"),
    HART_UNIT(68, "Newton"),
    HART_UNIT(69, "Newton Meter"),
    HART_UNIT(70, "Grams per Second"),
    HART_UNIT(71, "Grams per Minute"),
    HART_UNIT(72, "Grams per Hour"),
    HART_UNIT(73, "Kilograms per Second"),
    HART_UNIT(74, "Kilograms per Minute"),
    HART_UNIT(75, "Kilograms per Hour"),
    HART_UNIT(76, "Kilograms per Day"),
    HART_UNIT(77, "Metric Tons per Minute"),
    HART_UNIT(78, "Metric Tons per Hour"),
    HART_UNIT(79, "Metric Tons per Day"),
    HART_UNIT(80, "Pounds per Second"),
    HART_UNIT(81, "Pounds per Minute"),
    HART_UNIT(82, "Pounds per Hour"),
    HART_UNIT(83, "Pounds per Day"),
    HART_UNIT(84, "Short Tons per Minute"),
    HART_UNIT(85, "Short Tons per Hour"),
    HART_UNIT(86, "Short Tons per Day"),
    HART_UNIT(87, "Long Tons per Hour"),
    HART_UNIT(88, "Long Tons per Day"),
    HART_UNIT(89, "Deka Therm"),
    HART_UNIT(90, "Specific Gravity Units"),
    HART_UNIT(91, "Grams per Cubic Centimeter"),
    HART_UNIT(92, "Kilograms per Cubic Meter"),
    HART_UNIT(93, "Pounds per Gallon"),
    HART_UNIT(94, "Pounds per Cubic Foot"),
    HART_UNIT(95, "Grams per Milliliter"),
    HART_UNIT(96, "Kilograms per Liter"),
    HART_UNIT(97, "Grams per Liter"),
    HART_UNIT(98, "Pounds per Cubic Inch"),
    HART_UNIT(99, "Short Tons per Cubic Yard"),
    HART_UNIT(100, "Degree Twaddell"),
    HART_UNIT(101, "Degree Brix"),
    HART_UNIT(102, "Degree Baume Heavy"),
    HART_UNIT(103, "Degree Baume Light"),
    HART_UNIT(104, "Degree Api"),
    HART_UNIT(105, "Percent Solids per Weight"),
    HART_UNIT(106, "Percent Solids per Volume"),
    HART_UNIT(107, "Degree Balling"),
    HART_UNIT(108, "Proof per Volume"),
    HART_UNIT(109, "Proof per Mass"),
    HART_UNIT(110, "Buchel"),
    HART_UNIT(111, "Cubic Yards"),
    HART_UNIT(112, "Cubic Feet"),
    HART_UNIT(113, "Cubic Inches"),
    HART_UNIT(114, "Inches per Second"),
    HART_UNIT(115, "Inches per Minute"),
    HART_UNIT(116, "Feet per Minute"),
    HART_UNIT(117, "Degree per Second"),
    HART_UNIT(118, "Revolution per Second"),
    HART_UNIT(119, "Revolution per Minute"),
    HART_UNIT(120, "Meters per Hour"),
    HART_UNIT(121, "Normal Cubic Meter per Hour"),
    HART_UNIT(122, "Normal Liter per Hour"),
    HART_UNIT(123, "Standard Cubic Feet per Minute"),
    HART_UNIT(124, "Liquid Barres"),
    HART_UNIT(125, "Ounce"),
    HART_UNIT(126, "Foot Pound Force"),
    HART_UNIT(127, "Kilowatt"),
    HART_UNIT(128, "Kilowatt hour"),
    HART_UNIT(129, "Horsepower"),
    HART_UNIT(130, "Cubic Feet per Hour"),
    HART_UNIT(131, "Cubic Meters per Minute"),
    HART_UNIT(132, "Barrels per Second"),
    HART_UNIT(133, "Barrels per Minute"),
    HART_UNIT(134, "Barrels per Hour"),
    HART_UNIT(135, "Barrels per Day"),
    HART_UNIT(136, "Gallons per Hour"),
    HART_UNIT(137, "Imperial Gallons per Second"),
    HART_UNIT(138, "Liters per Hour"),
    HART_UNIT(139, "Parts per Million"),
    HART_UNIT(140, "Megacalorie per Hour"),
    HART_UNIT(141, "Megajoule per Hour"),
    HART_UNIT(142, "British Thermal Unit per Hour"),
    HART_UNIT(143, "Degree"),
    HART_UNIT(144, "Radian"),
    HART_UNIT(145, "Inches H2O 60F"),
    HART_UNIT(146, "Micrograms per Liter"),
    HART_UNIT(147, "Micrograms per Cubic Meter"),
    HART_UNIT(148, "Percent Consistency"),
    HART_UNIT(149, "Volume Percent"),
    HART_UNIT(150, "Percent Steam Quality"),
    HART_UNIT(151, "Feet in Sixteenths"),
    HART_UNIT(152, "Cubic Feet per Pound"),
    HART_UNIT(153, "Picofarads"),
    HART_UNIT(154, "Milliliters per Liter"),
    HART_UNIT(155, "Microliters per Liter"),
    HART_UNIT(160, "Percent Plato"),
    HART_UNIT(161, "Percent Lower Explosion Level"),
    HART_UNIT(162, "Megacalorie"),
    HART_UNIT(163, "Kilo Ohms"),
    HART_UNIT(164, "Megajoule"),
    HART_UNIT(165, "British Thermal Unit"),
    HART_UNIT(166, "Normal Cubic Meter"),
    HART_UNIT(167, "Normal Liter"),
    HART_UNIT(168, "Standard Cubic Feet"),
    HART_UNIT(169, "Parts per Billion"),
    HART_UNIT(235, "Gallons per Day"),
    HART_UNIT(236, "Hectoliters"),
    HART_UNIT(237, "Megapascal"),
    HART_UNIT(238, "Inches H2O 4C"),
    HART_UNIT(239, "Millimiter H2O 4C"),
    HART_UNIT(251, "None"),
    HART_UNIT(253, "Free unit Text")]

#
# get unit name from code
#
def GetUnitString(unit_code):
    for idx in range(len(ALL_HART_UNITS)):
        if (ALL_HART_UNITS[idx].untcode == unit_code):
            return ALL_HART_UNITS[idx].name
    return "Invalid Unit Code"

#
# get unit code from name
#
def GetUnitCode(unit_name):
    for idx in range(len(ALL_HART_UNITS)):
        if (ALL_HART_UNITS[idx].name == unit_name):
            return ALL_HART_UNITS[idx].untcode
    return 255


"""
-------------------------------------------------------------------------------
DEVICE PROFILE
-------------------------------------------------------------------------------
"""

#
# profile [code + name]
#
class PROFILE():
    def __init__(self, _prof_code, _name):
        self.prof_code = _prof_code
        self.name = _name

#
# array of all device profiles
#
DEVICE_PROFILES = [
    PROFILE(1, "Process Automation Device"),
    PROFILE(2, "Discrete Device"),
    PROFILE(3, "Hybrid: Process Automation + Discrete"),
    PROFILE(4, "I/O System"),
    PROFILE(14, "Discrete Adapter"),
    PROFILE(129, "WirelessHART Process Automation Device"),
    PROFILE(130, "WirelessHART Discrete Device"),
    PROFILE(131, "WirelessHART Hybrid: Process Automation + Discrete"),
    PROFILE(132, "WirelessHART Gateway"),
    PROFILE(140, "WirelessHART Access Point"),
    PROFILE(141, "WirelessHART Process Adapter"),
    PROFILE(142, "WirelessHART Discrete Adapter"),
    PROFILE(144, "WirelessHART-Enable Handheld/Portable Maintenance Tool")]

#
# get profile given the code
#
def GetProfileString(prof_code):
    for idx in range(len(DEVICE_PROFILES)):
        if (DEVICE_PROFILES[idx].prof_code == prof_code):
            return DEVICE_PROFILES[idx].name
    return "None"


"""
-------------------------------------------------------------------------------
EXTENDED FIELD DEVICE STATUS
-------------------------------------------------------------------------------
"""
#
# Get extended field device status string
#
def GetExtendedFieldDeviceStatus(status):
    desc = []
    if ((status & 0x01) == 0x01):
        desc.append("Maintenance Required")
    
    if ((status & 0x02) == 0x02):
        desc.append("Device Variable Alert")
    
    if ((status & 0x04) == 0x04):
        desc.append("Critical Power Failure")
    
    if ((status & 0x08) == 0x08):
        desc.append("Failure")
        
    if ((status & 0x10) == 0x10):
        desc.append("Out of Specification")
    
    if ((status & 0x20) == 0x20):
        desc.append("Function Check")
        
    return desc
  
    
"""
-------------------------------------------------------------------------------
PHYSICAL SIGNALING CODES - HW REV LEVEL
-------------------------------------------------------------------------------
"""
#
# signals [code + name]
#
class SIGNAL():
    def __init__(self, _sig_code, _name):
        self.sig_code = _sig_code
        self.name = _name

#
# array of all signals
#
SIGNALS = [
    SIGNAL(0, "Bell 202 Current"),
    SIGNAL(1, "Bell 202 Voltage"),
    SIGNAL(2, "RS-485"),
    SIGNAL(3, "RS-232"),
    SIGNAL(4, "Wireless [NB \"Unknown\" for HART revision 5 and 6]"),
    SIGNAL(6, "Special (includes, for example, Ethernet, TCP/IP, WiFi, etc.)")]

#
# get signal given the code
#
def GetSignalString(commandZeroByte7):
    sig_code = commandZeroByte7 & 7 # 7 -> (111b) = last significant 3 bits of commandZeroByte7
    for idx in range(len(SIGNALS)):
        if (SIGNALS[idx].sig_code == sig_code):
            return SIGNALS[idx].name
    return "Unknown"
    
def GetHardwareRevisionLevel(commandZeroByte7):
    hwLev = commandZeroByte7 & 248 # 248 -> (11111000b) = most significant 5 bits of commandZeroByte7
    return (hwLev >> 3)


"""
-------------------------------------------------------------------------------
COMMUNICATION ERRORS
-------------------------------------------------------------------------------
"""

#
# get communicaton errors from response code
#
def hasCommunicationErrors(resCode):
    desc = []
    if (resCode > 0x80):
        if ((resCode & 0x40) == 0x40):
            desc.append("Vertical Parity Error - The parity of one or more of the bytes received by the device was not odd.")

        if ((resCode & 0x20) == 0x20):
            desc.append("Overrun Error - At least one byte of data in the receive buffer of the UART was overwritten before it was read (i.e., the slave did not process incoming byte fast enough).")

        if ((resCode & 0x10) == 0x10):
            desc.append("Framing Error - The Stop Bit of one or more bytes received by the device was not detected by the UART (i.e. a mark or 1 was not detected when a Stop Bit should have occoured).")

        if ((resCode & 0x08) == 0x08):
            desc.append("Longitudinal Partity Error - The Longitudinal Partity calculated by the device did not match the Check Byte at the end of the message.")

        if ((resCode & 0x02) == 0x02):
            desc.append("Buffer Overflow - The message was too long for the receive buffer of the device.")
    
    return desc


"""
-------------------------------------------------------------------------------
DEVICE STATUS
-------------------------------------------------------------------------------
"""
#
# get active device status in text format
#
def GetDevStatusDesc(devStatus):
    meanings = []
    if ((devStatus & 0x80) == 0x80):
        meanings.append("Device Malfunction")

    if ((devStatus & 0x40) == 0x40):
        meanings.append("Configuration Changed")

    if ((devStatus & 0x20) == 0x20):
        meanings.append("Cold Start")

    if ((devStatus & 0x10) == 0x10):
        meanings.append("More Status Available")

    if ((devStatus & 0x08) == 0x08):
        meanings.append("Current Fixed")

    if ((devStatus & 0x04) == 0x04):
        meanings.append("Current Saturated")

    if ((devStatus & 0x02) == 0x02):
        meanings.append("Non PV Out of Limits")

    if ((devStatus & 0x01) == 0x01):
        meanings.append("PV Out of Limits")

    return meanings


"""
-------------------------------------------------------------------------------
DEVICE FLAGS
-------------------------------------------------------------------------------
"""

#
# get device flags in text format from flags field in HART command zero
#
def GetDevFlags(_flags):
    flags = []
    
    if (_flags == 0x00):
        flags.append("No flags")
    else:
        if ((_flags & 0x01) == 0x01):
            flags.append("Multi-Sensor Field Device")

        if ((_flags & 0x02) == 0x02):
            flags.append("EEPROM Control")

        if ((_flags & 0x04) == 0x04):
            flags.append("Protocol Bridge Device")

        if ((_flags & 0x08) == 0x08):
            flags.append("IEEE 802.15.4 2.4GHz DSSS with O-QPSK Modulation")

        if ((_flags & 0x40) == 0x40):
            flags.append("C8PSK Capable Field Device")

        if ((_flags & 0x80) == 0x80):
            flags.append("C8PSK In Multi-Drop Only")

    return flags


"""
-------------------------------------------------------------------------------
PRINT DEVICE
-------------------------------------------------------------------------------
"""
#
# Shows device information using previous functions
#
def PrintDevice(dev, hart):
    #print("-------------------------------------------------------------------------------")
    print("[DEVICE]")
    dev.printDev()
    print("\n")
    
"""
-------------------------------------------------------------------------------
PRINT PACKET
-------------------------------------------------------------------------------
"""
#
# Print a packet, useful if wantToPrint is False in Comm
#
def PrintPacket(packet, hart):            
    if (packet.isTxPacket() == False) and (packet.isBurstPacket() == False) and (((hart.masterType == MASTER_TYPE.PRIMARY) and ((packet.address[0] & 0x80) == 0)) or ((hart.masterType == MASTER_TYPE.SECONDARY) and ((packet.address[0] & 0x80) > 0))):
        #print("-------------------------------------------------------------------------------")
        print("[SLAVE TO MASTER - OACK]")
        packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
        
    elif (packet.isTxPacket() == False) and (packet.isBurstPacket() == False):
        #print("-------------------------------------------------------------------------------")
        print("[SLAVE TO MASTER - ACK]")
        packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
        
    elif (packet.isBurstPacket() == True):
        if (hart.masterType == MASTER_TYPE.PRIMARY):
            if ((packet.address[0] & 0x80) == 1):
                #print("-------------------------------------------------------------------------------")
                print("[BURST FRAME - BACK]")
                packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            else:
                #print("-------------------------------------------------------------------------------")
                print("[BURST FRAME - OBACK]")
                packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
        else:
            if ((packet.address[0] & 0x80) == 0):
                #print("-------------------------------------------------------------------------------")
                print("[BURST FRAME - BACK]")
                packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            else:
                #print("-------------------------------------------------------------------------------")
                print("[BURST FRAME - OBACK]")
                packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
        
    elif (packet.isTxPacket() == True) and (((hart.masterType == MASTER_TYPE.PRIMARY) and ((packet.address[0] & 0x80) == 0)) or ((hart.masterType == MASTER_TYPE.SECONDARY) and ((packet.address[0] & 0x80) > 0))):
        #print("-------------------------------------------------------------------------------")
        print("[MASTER TO SLAVE - OSTX]")
        packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
    
    elif (packet.isTxPacket() == True):
        #print("-------------------------------------------------------------------------------")
        print("[MASTER TO SLAVE - STX]")
        packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
        
    else:
        #print("-------------------------------------------------------------------------------")
        print("[UNKNOWN PACKET]")
        packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)

    print("\n")
    

"""
-------------------------------------------------------------------------------
COMMUNICATION ERROR CODE DECODE STRING
-------------------------------------------------------------------------------
"""
#
# gets the meaning of a communication result error code
#
def GetCommErrorString(error):
    if (error != None):
        if (error == 0):
            return "Ok"
        elif (error == 1):
            return "No response"
        elif (error == 2):
            return "Checksum error"
        elif (error == 3):
            return "Frame error"
        elif (error == 4):
            return "Synchronizing"
        else:
            return "Unknown error code"
    else:
        return "Unknown error code"


"""
-------------------------------------------------------------------------------
PACKED ASCII CHARACTER SET
-------------------------------------------------------------------------------
"""
def print_packedascii_charset():
    print('@  A  B  C  D  E  F  G  H  I  J  K  L  M  N  O')
    print('P  Q  R  S  T  U  V  W  X  Y  Z  [  \  ]  ^  _')
    print('SP !  \"  #  $  %  &amp;  \'  (  )  *  +  ,  -  .  /')
    print('0  1  2  3  4  5  6  7  8  9  :  ;  &lt;  =  &gt;  ?')

def get_packedascii_charset():
    charset = ['@',  'A',  'B',  'C',  'D',  'E',  'F',  'G',  'H',  'I',  'J',  'K',  'L',  'M',  'N',  'O',
               'P', 'Q',  'R',  'S',  'T',  'U',  'V',  'W',  'X',  'Y',  'Z',  '[',  '\\',  ']',  '^',  '_',
               ' ', '!',  '"',  '#',  '$',  '%',  '&',  '\'',  '(',  ')',  '*',  '+',  ',',  '-',  '.',  '/',
               '0',  '1',  '2',  '3',  '4',  '5',  '6',  '7',  '8',  '9',  ':',  ';',  '<',  '=',  '>',  '?']
    return charset


"""
-------------------------------------------------------------------------------
HART COMMANDS EXEC
-------------------------------------------------------------------------------
"""
#
# Useful function printing command result after fast analysis of the result.
#
def HartCommand(hart, cmdNum, txData):
    retStatus = False
    CommunicationResult, SentPacket, RecvPacket = hart.PerformTransaction(cmdNum, txData)
    if (CommunicationResult != None) and (CommunicationResult != CommResult.Ok):    
        print("HART command " + str(cmdNum) + ": " + GetCommErrorString(CommunicationResult))
    else:
        if (RecvPacket != None) and (RecvPacket.resCode != 0):
            print("HART command " + str(cmdNum) + ": " + "Response Code = " + str(RecvPacket.resCode))
        elif (RecvPacket == None):
            print("HART command " + str(cmdNum) + ": " + "Unknown Error!")
        else:
            retStatus = True
    
    return retStatus, CommunicationResult, SentPacket, RecvPacket
