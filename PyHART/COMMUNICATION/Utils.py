###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
from serial.tools import list_ports
from PyHART.COMMUNICATION.Common import *

class Table10:
    index = 10
    name = 'Physical Signaling Codes'

    values = {
        0: ['0', 'Bell 202 Current'],
        1: ['1', 'Bell 202 Voltage'],
        2: ['2', 'RS-485'],
        3: ['3', 'RS-232'],
        4: ['4', 'Wireless [NB \'Unknown\' for HART revision 5 and 6]'],
        5: ['6', 'Special (includes, for example, Ethernet, TCP/IP, WiFi, etc.)']
    }
    
    def get_desc(index):
        idx = str(index)
        desc = 'Value not in table.'
        for key in Table10.values:
            if idx == Table10.values[key][0]:
                desc = Table10.values[key][1]
                break

        return desc

        
    def WriteValues():
        val = 0
        desc = 1
        
        print(Table10.name)
        for key in Table10.values:
            print(f'{Table10.values[key][val]} : {Table10.values[key][desc]}')
        
        print('\n')

class Table11:
    index = 11
    name = 'Flag Assignments'

    values = {
        0: ['0x01', 'Multi-Sensor Field Device'],
        1: ['0x02', 'EEPROM Control'],
        2: ['0x04', 'Protocol Bridge Device'],
        3: ['0x08', 'IEEE 802.15.4 2.4GHz DSSS with O-QPSK Modulation'],
        4: ['0x40', 'C8PSK Capable Field Device'],
        5: ['0x80', 'C8PSK In Multi-Drop Only']
    }
    
    def get_desc(index):
        idx = f'0x{index:02X}'
        desc = 'Value not in table.'
        for key in Table11.values:
            if idx == Table11.values[key][0]:
                desc = Table11.values[key][1]
                break

        return desc

        
    def WriteValues():
        val = 0
        desc = 1
        
        print(Table11.name)
        for key in Table11.values:
            print(f'{Table11.values[key][val]} : {Table11.values[key][desc]}')
        
        print('\n')


    def GetActiveMask(_mask):
        maskDesc = []

        for key in Table11.values:
            code = int(Table11.values[key][0], 16)
            if ((_mask & code) == code):
                maskDesc.append(Table11.get_desc(code))

        return maskDesc

class Table57:
    index = 57
    name = 'Device Profile Codes'
    
    values = {
        0: ['1', 'Process Automation Device'],
        1: ['2', 'Discrete Device'],
        2: ['3', 'Hybrid: Process Automation + Discrete'],
        3: ['4', 'I/O System'],
        4: ['14', 'Discrete Adapter'],
        5: ['65', 'HART-IP Process Automation Device'],
        6: ['66', 'HART-IP Discrete Device'],
        7: ['67', 'HART-IP Hybrid: Process Automation + Discrete'],
        8: ['68', 'HART-IP I/O System'],
        9: ['129', 'WirelessHART Process Automation Device'],
        10: ['130', 'WirelessHART Discrete Device'],
        11: ['131', 'WirelessHART Hybrid: Process Automation + Discrete'],
        12: ['132', 'WirelessHART Gateway'],
        13: ['140', 'WirelessHART Access Point'],
        14: ['141', 'WirelessHART Process Adapter'],
        15: ['142', 'WirelessHART Discrete Adapter'],
        16: ['144', 'WirelessHART-Enable Handheld/Portable Maintenance Tool']
    }
    
    def get_desc(index):
        idx = str(index)
        desc = 'Value not in table.'
        for key in Table57.values:
            if idx == Table57.values[key][0]:
                desc = Table57.values[key][1]
                break
        return desc

        
    def WriteValues():
        val = 0
        desc = 1
        
        print(Table57.name)
        for key in Table57.values:
            print(f'{Table57.values[key][val]} : {Table57.values[key][desc]}')
        
        print('\n')

class Table17:
    index = 17
    name = 'Extended Device Status'

    values = {
        0: ['0x01', 'Maintenance Required'],
        1: ['0x02', 'Device Variable Alert'],
        2: ['0x04', 'Critical Power Failure'],
        3: ['0x08', 'Failure'],
        4: ['0x10', 'Out of Specification'],
        5: ['0x20', 'Function Check']
    }
    
    def get_desc(index):
        idx = f'0x{index:02X}'
        desc = 'Value not in table.'
        for key in Table17.values:
            if idx == Table17.values[key][0]:
                desc = Table17.values[key][1]
                break

        return desc

        
    def WriteValues():
        val = 0
        desc = 1
        
        print(Table17.name)
        for key in Table17.values:
            print(f'{Table17.values[key][val]} : {Table17.values[key][desc]}')
        
        print('\n')


    def GetActiveMask(_mask):
        maskDesc = []

        for key in Table17.values:
            code = int(Table17.values[key][0], 16)
            if ((_mask & code) == code):
                maskDesc.append(Table17.get_desc(code))

        return maskDesc

class Table2:
    index = 2
    name = 'Engineering Unit Codes'
    
    values = {
        0	: ['1', 'Inches H2O 68F'],				
        1	: ['2', 'Inches HG 0C'],				
        2	: ['3', 'Feet H2O 68F'],				
        3	: ['4', 'Millimiter H2O 68F'],				
        4	: ['5', 'Millimiter HG'],				
        5	: ['6', 'Psi'],				
        6	: ['7', 'Bar'],				
        7	: ['8', 'Millibar'],				
        8	: ['9', 'Gram per Centimeter^2'],				
        9	: ['10', 'Kilogram per Centimeter^2'],				
        10	: ['11', 'Pascal'],				
        11	: ['12', 'Kilopascal'],				
        12	: ['13', 'Torr'],				
        13	: ['14', 'Atmosphere'],				
        14	: ['15', 'Cubic Feet per Minute'],				
        15	: ['16', 'Gallons per Minute'],				
        16	: ['17', 'Liters per Minute'],				
        17	: ['18', 'Imperial Gallons per Minute'],				
        18	: ['19', 'Cubic Meter per Hour'],				
        19	: ['20', 'Feet per Second'],				
        20	: ['21', 'Meter per Second'],				
        21	: ['22', 'Gallons per Second'],				
        22	: ['23', 'Million Gallons per Day'],				
        23	: ['24', 'Liters per Second'],				
        24	: ['25', 'Million Liters per Day'],				
        25	: ['26', 'Cubic Feet per Second'],				
        26	: ['27', 'Cubic Feet per Day'],				
        27	: ['28', 'Cubic Meter per Second'],				
        28	: ['29', 'Cubic Meter per Day'],				
        29	: ['30', 'Imperial Gallons per Hour'],				
        30	: ['31', 'Imperial Gallons per Day'],				
        31	: ['32', 'Celsius'],				
        32	: ['33', 'Fahrenheit'],				
        33	: ['34', 'Rankine'],				
        34	: ['35', 'Kelvin'],				
        35	: ['36', 'Millivolts'],				
        36	: ['37', 'Ohms'],				
        37	: ['38', 'Hertz'],				
        38	: ['39', 'Milliampere'],				
        39	: ['40', 'Gallons'],				
        40	: ['41', 'Liters'],				
        41	: ['42', 'Imperial Gallons'],				
        42	: ['43', 'Cubic Meters'],				
        43	: ['44', 'Feet'],				
        44	: ['45', 'Meter'],				
        45	: ['46', 'Barrels'],				
        46	: ['47', 'Inch'],				
        47	: ['48', 'Centimeter'],				
        48	: ['49', 'Millimeter'],				
        49	: ['50', 'Minutes'],				
        50	: ['51', 'Seconds'],				
        51	: ['52', 'Hours'],				
        52	: ['53', 'Day'],				
        53	: ['54', 'Centistokes'],				
        54	: ['55', 'Centipoise'],				
        55	: ['56', 'Microsiemens'],				
        56	: ['57', 'Percent'],				
        57	: ['58', 'Volts'],				
        58	: ['59', 'Ph'],				
        59	: ['60', 'Grams'],				
        60	: ['61', 'Kilograms'],				
        61	: ['62', 'Metric Tons'],				
        62	: ['63', 'Pounds'],				
        63	: ['64', 'Short Tons'],				
        64	: ['65', 'Long Tons'],				
        65	: ['66', 'Millisiemens per centimeter'],				
        66	: ['67', 'Microsiemens per centimeter'],				
        67	: ['68', 'Newton'],				
        68	: ['69', 'Newton Meter'],				
        69	: ['70', 'Grams per Second'],				
        70	: ['71', 'Grams per Minute'],				
        71	: ['72', 'Grams per Hour'],				
        72	: ['73', 'Kilograms per Second'],				
        73	: ['74', 'Kilograms per Minute'],				
        74	: ['75', 'Kilograms per Hour'],				
        75	: ['76', 'Kilograms per Day'],				
        76	: ['77', 'Metric Tons per Minute'],				
        77	: ['78', 'Metric Tons per Hour'],				
        78	: ['79', 'Metric Tons per Day'],				
        79	: ['80', 'Pounds per Second'],				
        80	: ['81', 'Pounds per Minute'],				
        81	: ['82', 'Pounds per Hour'],				
        82	: ['83', 'Pounds per Day'],				
        83	: ['84', 'Short Tons per Minute'],				
        84	: ['85', 'Short Tons per Hour'],				
        85	: ['86', 'Short Tons per Day'],				
        86	: ['87', 'Long Tons per Hour'],				
        87	: ['88', 'Long Tons per Day'],				
        88	: ['89', 'Deka Therm'],				
        89	: ['90', 'Specific Gravity Units'],				
        90	: ['91', 'Grams per Cubic Centimeter'],				
        91	: ['92', 'Kilograms per Cubic Meter'],				
        92	: ['93', 'Pounds per Gallon'],				
        93	: ['94', 'Pounds per Cubic Foot'],				
        94	: ['95', 'Grams per Milliliter'],				
        95	: ['96', 'Kilograms per Liter'],				
        96	: ['97', 'Grams per Liter'],				
        97	: ['98', 'Pounds per Cubic Inch'],				
        98	: ['99', 'Short Tons per Cubic Yard'],				
        99	: ['100', 'Degree Twaddell'],				
        100	: ['101', 'Degree Brix'],				
        101	: ['102', 'Degree Baume Heavy'],				
        102	: ['103', 'Degree Baume Light'],				
        103	: ['104', 'Degree Api'],				
        104	: ['105', 'Percent Solids per Weight'],				
        105	: ['106', 'Percent Solids per Volume'],				
        106	: ['107', 'Degree Balling'],				
        107	: ['108', 'Proof per Volume'],				
        108	: ['109', 'Proof per Mass'],				
        109	: ['110', 'Buchel'],				
        110	: ['111', 'Cubic Yards'],				
        111	: ['112', 'Cubic Feet'],				
        112	: ['113', 'Cubic Inches'],				
        113	: ['114', 'Inches per Second'],				
        114	: ['115', 'Inches per Minute'],				
        115	: ['116', 'Feet per Minute'],				
        116	: ['117', 'Degree per Second'],				
        117	: ['118', 'Revolution per Second'],				
        118	: ['119', 'Revolution per Minute'],				
        119	: ['120', 'Meters per Hour'],				
        120	: ['121', 'Normal Cubic Meter per Hour'],				
        121	: ['122', 'Normal Liter per Hour'],				
        122	: ['123', 'Standard Cubic Feet per Minute'],				
        123	: ['124', 'Liquid Barres'],				
        124	: ['125', 'Ounce'],				
        125	: ['126', 'Foot Pound Force'],				
        126	: ['127', 'Kilowatt'],				
        127	: ['128', 'Kilowatt hour'],				
        128	: ['129', 'Horsepower'],				
        129	: ['130', 'Cubic Feet per Hour'],				
        130	: ['131', 'Cubic Meters per Minute'],				
        131	: ['132', 'Barrels per Second'],				
        132	: ['133', 'Barrels per Minute'],				
        133	: ['134', 'Barrels per Hour'],				
        134	: ['135', 'Barrels per Day'],				
        135	: ['136', 'Gallons per Hour'],				
        136	: ['137', 'Imperial Gallons per Second'],				
        137	: ['138', 'Liters per Hour'],				
        138	: ['139', 'Parts per Million'],				
        139	: ['140', 'Megacalorie per Hour'],				
        140	: ['141', 'Megajoule per Hour'],				
        141	: ['142', 'British Thermal Unit per Hour'],				
        142	: ['143', 'Degree'],				
        143	: ['144', 'Radian'],				
        144	: ['145', 'Inches H2O 60F'],				
        145	: ['146', 'Micrograms per Liter'],				
        146	: ['147', 'Micrograms per Cubic Meter'],				
        147	: ['148', 'Percent Consistency'],				
        148	: ['149', 'Volume Percent'],				
        149	: ['150', 'Percent Steam Quality'],				
        150	: ['151', 'Feet in Sixteenths'],				
        151	: ['152', 'Cubic Feet per Pound'],				
        152	: ['153', 'Picofarads'],				
        153	: ['154', 'Milliliters per Liter'],				
        154	: ['155', 'Microliters per Liter'],				
        155	: ['160', 'Percent Plato'],				
        156	: ['161', 'Percent Lower Explosion Level'],				
        157	: ['162', 'Megacalorie'],				
        158	: ['163', 'Kilo Ohms'],				
        159	: ['164', 'Megajoule'],				
        160	: ['165', 'British Thermal Unit'],				
        161	: ['166', 'Normal Cubic Meter'],				
        162	: ['167', 'Normal Liter'],				
        163	: ['168', 'Standard Cubic Feet'],				
        164	: ['169', 'Parts per Billion'],				
        165	: ['235', 'Gallons per Day'],				
        166	: ['236', 'Hectoliters'],				
        167	: ['237', 'Megapascal'],				
        168	: ['238', 'Inches H2O 4C'],				
        169	: ['239', 'Millimiter H2O 4C'],				
        170	: ['250', 'Not Used'],				
        171	: ['251', 'None'],				
        172	: ['252', 'Unknown'],				
        173	: ['253', 'Special']	
    }
    
    def get_desc(index):
        idx = str(index)
        desc = 'Value not in table.'
        found = False
        for key in Table2.values:
            if idx == Table2.values[key][0]:
                desc = Table2.values[key][1]
                found = True
                break

        if (found == False) and (index >= 240) and (index <= 249):
            desc = 'Enumeration May Be Used For Manufacturer Specific Definitions'
        elif (found == False) and (index >= 170) and (index <= 219):
            desc = 'This Code Could Assume Different Meanings Depending By Device Classification (Table 21), Check Protocol Specifications.'

        return desc

        
    def WriteValues():
        val = 0
        desc = 1
        
        print(Table2.name)
        for key in Table2.values:
            print(f'{Table2.values[key][val]} : {Table2.values[key][desc]}')

        print('Values In Range 240..249 May Be Used For Manufacturer Specific Definitions.')
        print('Values In Range 170..219 Could Assume Different Meanings Depending By Device Classification (Table 21), Check Protocol Specifications.')
        
        print('\n')


'''
-------------------------------------------------------------------------------
GET PY_HART REVISION
-------------------------------------------------------------------------------
'''
def PyHART_Revision():
    return '1.0'


'''
-------------------------------------------------------------------------------
BURST
-------------------------------------------------------------------------------
'''
#
# Indicates if a device is in burst or no by passing first byte of the address
# when you execute an hart command.
#
def isInBurst(address0):
    if ((address0 & 0x40) > 0):
        return True
    else:
        return False

'''
-------------------------------------------------------------------------------
COM PORTS
-------------------------------------------------------------------------------
'''
#
# ATTENTION: In revisions till the current, this function has been tested only under Windows OS
# This functions enumerates all available COM ports and add a incremental number before each port.
# This is useful if you want to create a menu.
# in addition it is possible if to add custom options to choose at the end of the list, for example
# if the user wants to leave the application you can add 'Quit'.
# This function returns the list of the ports and the count of found com ports.
# Additional options count is not included in the count.
#
def ListCOMPort(additionalOptions = None):
    print('\nAvailable COM ports')
    i = 1
    listOfComPorts = list_ports.comports()
    for portsInfo in enumerate(listOfComPorts):
        print('  {0}: '.format(i) + '{0} - {1}'.format(portsInfo[1].device, portsInfo[1].description))
        i += 1

    if additionalOptions != None:
        for j in range(len(additionalOptions)):
            print('  {0}: '.format(i) + additionalOptions[j])
            i += 1

    return len(listOfComPorts), listOfComPorts

#
#
#
def ListCOMPortWithoutPrint():
    retPorts = [[], []]
    
    listOfComPorts = list_ports.comports()
    for portsInfo in enumerate(listOfComPorts):
        retPorts[0].append(portsInfo[1].device)
        retPorts[1].append(portsInfo[1].description)

    return retPorts

#
# This function is used combined with 'ListCOMPort'.
# You can pass the user selection (of the incremental number) and the list of ports
# returned from ListCOMPort.
# This function returns the name of the port, for example 'COM1' or none if the selection is not valid.
#    
def GetCOMPort(sel, listOfComPorts):
    try:
        if (listOfComPorts is not None) and (sel > 0):
            i = 1
            for portsInfo in enumerate(listOfComPorts):
                if (i == sel):
                    return '{0}'.format(portsInfo[1].device)
                i += 1
    except:
        return None
        
    return None

'''
-------------------------------------------------------------------------------
MEASURAMENT UNITS
-------------------------------------------------------------------------------
'''
#
# get unit name from code
#
def GetUnitString(unit_code):
    return Table2.get_desc(unit_code)

'''
-------------------------------------------------------------------------------
DEVICE PROFILE
-------------------------------------------------------------------------------
'''
#
# get profile given the code
#
def GetProfileString(prof_code):
    return Table57.get_desc(prof_code)


'''
-------------------------------------------------------------------------------
EXTENDED FIELD DEVICE STATUS
-------------------------------------------------------------------------------
'''
#
# Get extended field device status string
#
def GetExtendedFieldDeviceStatus(status):
    return Table17.GetActiveMask(status)
  
    
'''
-------------------------------------------------------------------------------
PHYSICAL SIGNALING CODES - HW REV LEVEL
-------------------------------------------------------------------------------
'''
#
# get signal given the code
#
def GetSignalString(commandZeroByte7):
    sig_code = commandZeroByte7 & 7 # 7 -> (111b) = last significant 3 bits of commandZeroByte7
    return Table10.get_desc(sig_code)
    
def GetHardwareRevisionLevel(commandZeroByte7):
    hwLev = commandZeroByte7 & 248 # 248 -> (11111000b) = most significant 5 bits of commandZeroByte7
    return (hwLev >> 3)


'''
-------------------------------------------------------------------------------
COMMUNICATION ERRORS
-------------------------------------------------------------------------------
'''

#
# get communicaton errors from response code
#
def hasCommunicationErrors(resCode):
    desc = []
    if (resCode > 0x80):
        if ((resCode & 0x40) == 0x40):
            desc.append('Vertical Parity Error - The parity of one or more of the bytes received by the device was not odd.')

        if ((resCode & 0x20) == 0x20):
            desc.append('Overrun Error - At least one byte of data in the receive buffer of the UART was overwritten before it was read (i.e., the slave did not process incoming byte fast enough).')

        if ((resCode & 0x10) == 0x10):
            desc.append('Framing Error - The Stop Bit of one or more bytes received by the device was not detected by the UART (i.e. a mark or 1 was not detected when a Stop Bit should have occoured).')

        if ((resCode & 0x08) == 0x08):
            desc.append('Longitudinal Partity Error - The Longitudinal Partity calculated by the device did not match the Check Byte at the end of the message.')

        if ((resCode & 0x02) == 0x02):
            desc.append('Buffer Overflow - The message was too long for the receive buffer of the device.')
    
    return desc


'''
-------------------------------------------------------------------------------
DEVICE STATUS
-------------------------------------------------------------------------------
'''
#
# get active device status in text format
#
def GetDevStatusDesc(devStatus):
    meanings = []
    if ((devStatus & 0x80) == 0x80):
        meanings.append('Device Malfunction')

    if ((devStatus & 0x40) == 0x40):
        meanings.append('Configuration Changed')

    if ((devStatus & 0x20) == 0x20):
        meanings.append('Cold Start')

    if ((devStatus & 0x10) == 0x10):
        meanings.append('More Status Available')

    if ((devStatus & 0x08) == 0x08):
        meanings.append('Current Fixed')

    if ((devStatus & 0x04) == 0x04):
        meanings.append('Current Saturated')

    if ((devStatus & 0x02) == 0x02):
        meanings.append('Non PV Out of Limits')

    if ((devStatus & 0x01) == 0x01):
        meanings.append('PV Out of Limits')

    return meanings
    
    
'''
-------------------------------------------------------------------------------
VARIABLE STATUS
-------------------------------------------------------------------------------
'''
#
# get active device status in text format
#
def GetVariableStatusDesc(varStatus):
    # Bit 7, 6 (Goodness)
    STATUS_GOOD =          0xC0
    STATUS_FIXED =         0x80
    STATUS_POOR_ACCURACY = 0x40
    STATUS_BAD =           0x00

    # bit 5, 4 (limit status)
    STATUS_CONSTANT =      0x30
    STATUS_HI_LIMITED =    0x20
    STATUS_LO_LIMITED =    0x10
    STATUS_NO_LIMITED =    0x00
    
    # bit 3 (More Device Variable Status Available)
    # Set if expanded Device Family Status Command contains diagnostic
    # information that is useful to the Host Application. Must be reset to zero
    # if Device Variable does not support any Device Family.
    STATUS_MORE_DEVICE_VARIABLE_STATUS_AVAILABLE = 0x08
    
    # bit 2, 1, 0 (Device Family Specific Status)
    # Specified by corresponding Device Family. Must be reset to zero is Device Variable
    # does not support any Device Family.
    
    meanings = []
    if (varStatus & 0xC0) == STATUS_GOOD:
        meanings.append('GOOD')
   
    if (varStatus & 0xC0) == STATUS_FIXED:
        meanings.append('FIXED')
   
    if (varStatus & 0xC0) == STATUS_POOR_ACCURACY:
        meanings.append('POOR_ACCURACY')
       
    if (varStatus & 0xC0) == STATUS_BAD:
        meanings.append('BAD')
       
    if (varStatus & 0x30) == STATUS_CONSTANT:
        meanings.append('CONSTANT')
   
    if (varStatus & 0x30) == STATUS_HI_LIMITED:
        meanings.append('HI_LIMITED')
   
    if (varStatus & 0x30) == STATUS_LO_LIMITED:
        meanings.append('LO_LIMITED')
       
    if (varStatus & 0x30) == STATUS_NO_LIMITED:
        meanings.append('NO_LIMITED')
       
    if (varStatus & STATUS_MORE_DEVICE_VARIABLE_STATUS_AVAILABLE) == STATUS_MORE_DEVICE_VARIABLE_STATUS_AVAILABLE:
        meanings.append('MORE_DEVICE_VARIABLE_STATUS_AVAILABLE (device specific bits 0, 1 and 2 of the variable status)')

    return meanings

'''
-------------------------------------------------------------------------------
DEVICE FLAGS
-------------------------------------------------------------------------------
'''

#
# get device flags in text format from flags field in HART command zero
#
def GetDevFlags(_flags):
    return Table11.GetActiveMask(_flags)


'''
-------------------------------------------------------------------------------
PRINT DEVICE
-------------------------------------------------------------------------------
'''
#
# Shows device information using previous functions
#
def PrintDevice(dev, hart):
    with globalPrintActivityLock:
        print('[DEVICE]')
        dev.printDev()
        print('')
    
'''
-------------------------------------------------------------------------------
PRINT PACKET
-------------------------------------------------------------------------------
'''
#
# Print a packet, useful if wantToPrint is False in Comm
#
def PrintPacket(packet, hart): 
    with globalPrintActivityLock:    
        if (packet.isTxPacket() == False) and (packet.isBurstPacket() == False) and (((hart.masterType == MASTER_TYPE.PRIMARY) and ((packet.address[0] & 0x80) == 0)) or ((hart.masterType == MASTER_TYPE.SECONDARY) and ((packet.address[0] & 0x80) > 0))):
            print('[SLAVE TO MASTER - OACK]')
            packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            
        elif (packet.isTxPacket() == False) and (packet.isBurstPacket() == False):
            print('[SLAVE TO MASTER - ACK]')
            packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            
        elif (packet.isBurstPacket() == True):
            if (hart.masterType == MASTER_TYPE.PRIMARY):
                if ((packet.address[0] & 0x80) == 1):
                    print('[BURST FRAME - BACK]')
                    packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
                else:
                    print('[BURST FRAME - OBACK]')
                    packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            else:
                if ((packet.address[0] & 0x80) == 0):
                    print('[BURST FRAME - BACK]')
                    packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
                else:
                    print('[BURST FRAME - OBACK]')
                    packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            
        elif (packet.isTxPacket() == True) and (((hart.masterType == MASTER_TYPE.PRIMARY) and ((packet.address[0] & 0x80) == 0)) or ((hart.masterType == MASTER_TYPE.SECONDARY) and ((packet.address[0] & 0x80) > 0))):
            #print('-------------------------------------------------------------------------------', end = '')
            print('[MASTER TO SLAVE - OSTX]')
            packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
        
        elif (packet.isTxPacket() == True):
            #print('-------------------------------------------------------------------------------', end = '')
            print('[MASTER TO SLAVE - STX]')
            packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)
            
        else:
            print('[UNKNOWN PACKET]')
            packet.printPkt(STEP_RX.STEP_CHECKSUM, hart.OnlineDevice)

        print('')
    

'''
-------------------------------------------------------------------------------
COMMUNICATION ERROR CODE DECODE STRING
-------------------------------------------------------------------------------
'''
#
# gets the meaning of a communication result error code
#
def GetCommErrorString(error):
    if (error != None):
        if (error == 0):
            return 'Ok'
        elif (error == 1):
            return 'No response'
        elif (error == 2):
            return 'Checksum error'
        elif (error == 3):
            return 'Frame error'
        elif (error == 4):
            return 'Synchronizing'
        else:
            return 'Unknown error code'
    else:
        return 'Unknown error code'


'''
-------------------------------------------------------------------------------
PACKED ASCII CHARACTER SET
-------------------------------------------------------------------------------
'''
def print_packedascii_charset():
    with globalPrintActivityLock:
        print('@  A  B  C  D  E  F  G  H  I  J  K  L  M  N  O')
        print('P  Q  R  S  T  U  V  W  X  Y  Z  [  \  ]  ^  _')
        print('SPACE !  \"  #  $  %  &  \'  (  )  *  +  ,  -  .  /')
        print('0  1  2  3  4  5  6  7  8  9  :  ;  <  =  >  ?')

def get_packedascii_charset():
    charset = ['@',  'A',  'B',  'C',  'D',  'E',  'F',  'G',  'H',  'I',  'J',  'K',  'L',  'M',  'N',  'O',
               'P', 'Q',  'R',  'S',  'T',  'U',  'V',  'W',  'X',  'Y',  'Z',  '[',  '\\',  ']',  '^',  '_',
               ' ', '!',  '"',  '#',  '$',  '%',  '&',  '\'',  '(',  ')',  '*',  '+',  ',',  '-',  '.',  '/',
               '0',  '1',  '2',  '3',  '4',  '5',  '6',  '7',  '8',  '9',  ':',  ';',  '<',  '=',  '>',  '?']
    return charset


'''
-------------------------------------------------------------------------------
HART COMMANDS EXEC
-------------------------------------------------------------------------------
'''
#
# Useful function printing command result after fast analysis of the result.
#
def HartCommand(hart, cmdNum, txData):
    retStatus = False
    CommunicationResult, SentPacket, RecvPacket = hart.PerformTransaction(cmdNum, txData)
    
    if CommunicationResult != None:
        with globalPrintActivityLock:
            if CommunicationResult == CommResult.Ok:
                if RecvPacket != None:
                    if RecvPacket.resCode != 0:
                        errors = hasCommunicationErrors(RecvPacket.resCode)
                        i = len(errors)
                        for idx in range(i):
                            print(errors[idx])
                        
                        if RecvPacket.resCode != 64:
                            print('HART command {0}: Response Code = {1}'.format(cmdNum, RecvPacket.resCode))
                        else:
                            print('HART command {0}: Response Code = {1}, Command Not Implemented.'.format(cmdNum, RecvPacket.resCode))
                        
                    if (((RecvPacket.command != 31) and (RecvPacket.dataLen >= 2)) or (((RecvPacket.command == 31) and (RecvPacket.dataLen >= 4)))):
                        if RecvPacket.resCode == 0:
                            retStatus = True
                    else:
                        print('HART command {0}: Data lenght mismatch'.format(cmdNum))
                else:
                    print('HART command {0}: Unknown Error'.format(cmdNum))
                    
            else:
                print('HART command {0}: '.format(cmdNum) + GetCommErrorString(CommunicationResult))
    else:
        with globalPrintActivityLock:
            print('HART command {0}: '.format(cmdNum) + GetCommErrorString(CommunicationResult))
    
    return retStatus, CommunicationResult, SentPacket, RecvPacket











