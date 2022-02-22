#
# In this module is shown how to send a command to an HART device.
# Encode/decode data, logging and manage responses codes.
# 


'''
-------------------------------------------------------------------------------
SAME CODE OF EXAMPLE 01 - IGNORE THIS SECTION
This is included to test the example
-------------------------------------------------------------------------------
'''
#
# Standard import. Append the path of PyHART. Since this file is in the folder PyHART_tutorial,
# just go back one folder.
#
import sys
sys.path.append('../')
from PyHART.COMMUNICATION.CommCore import *
from PyHART.COMMUNICATION.Types import *
from PyHART.COMMUNICATION.Utils import *
from PyHART.COMMUNICATION.Device import *
from PyHART.COMMUNICATION.Packet import *
from PyHART.COMMUNICATION.Common import *

#
# Procedure to list communication ports
#
count, listOfComPorts = ListCOMPort(True)
comport = None
selection = 0
while (comport == None) and (selection != (count + 1)):
    print ('\nSelect the communication port.') 
    print('Insert the number related to your choice and press enter.')
    try:
        selection = int(input())
    except:
        selection = 0
    
    if (selection == (count + 1)):
        print('Leaving application...')
        sys.exit()
    
    comport = GetCOMPort(selection, listOfComPorts)


#
# Instantiates and starts the communication object
#
hart = HartMaster(comport, \
                  MASTER_TYPE.PRIMARY, \
                  num_retry = 2, \
                  retriesOnPolling = False, \
                  autoPrintTransactions = True, \
                  whereToPrint = WhereToPrint.BOTH, \
                  logFile = 'terminalLog.log', \
                  rt_os = False, \
                  manageRtsCts = None)

hart.Start()


#
# Polling connected devices in range [0..EndPollingAddress] and 
# print identification data of the first device found.
#
FoundDevice = None
pollAddress = 0
EndPollingAddress = 3

while (FoundDevice == None) and (pollAddress < EndPollingAddress):
    CommunicationResult, SentPacket, RecvPacket, FoundDevice = hart.LetKnowDevice(pollAddress)
    pollAddress += 1

if (FoundDevice is not None):
    PrintDevice(FoundDevice, hart)
else:
    print ('Device not found. Leaving Application...')
    sys.exit()
'''
-------------------------------------------------------------------------------
END OF EXAMPLE 01 CODE
-------------------------------------------------------------------------------
'''


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Send command 15 and decode received data
# if retStatus is True it means 
# - CommunicationResult is OK
# - Response code is 0 (OK)
#
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 15, None)
if (retStatus == True):
    URV = BytearrayToFloat(RecvPacket.data[3:7])
    LRV = BytearrayToFloat(RecvPacket.data[7:11])
    Unit = RecvPacket.data[2]        
    print('URV: {0}'.format(URV))
    print('LRV: {0}'.format(LRV))
    print('Unit: ' + GetUnitString(Unit) + '\n')
    print(GetCommErrorString(CommunicationResult) + '\n')
    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# The same of previous with logging disabled
#
hart.autoPrintTransactions = False

retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 15, None)
if (retStatus == True):
    URV = BytearrayToFloat(RecvPacket.data[3:7])
    LRV = BytearrayToFloat(RecvPacket.data[7:11])
    Unit = RecvPacket.data[2]        
    print('URV: {0}'.format(URV))
    print('LRV: {0}'.format(LRV))
    print('Unit: ' + GetUnitString(Unit) + '\n')
    print(GetCommErrorString(CommunicationResult) + '\n')

hart.autoPrintTransactions = True


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# In case logging is disabled but you want to print a particular transaction
#
hart.autoPrintTransactions = False

retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 1, None)
if (retStatus == True):
    print('---------------- TRANSMITTED ----------------')
    PrintPacket(SentPacket, hart)
    print('---------------- RECEIVED ----------------')
    PrintPacket(RecvPacket, hart)

hart.autoPrintTransactions = True


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Send command 35, commad 18 and 13 encode/decode data example
# A decode example has been shown in previous command 15
#
txdata = bytearray(9)
txdata[0] = GetUnitCode('Kilopascal')
txdata[1:] = FloatToBytearray(120.43)
txdata[5:] = FloatToBytearray(-120.43)
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 35, txdata)

txdata = bytearray(21)
txdata[0:] = PackAscii('NEW TAG')
txdata[6:] = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
txdata[18:] = DateStringToBytearray('05/11/2016')
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 18, txdata)

if (retStatus == True):
    retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 13, None)
    if (retStatus == True):
        tag = UnpackAscii(RecvPacket.data[0:6])
        date = BytearrayToDateString(RecvPacket.data[18:21])                
        print('read tag: [{0}], read date: [{1}]\n'.format(tag, date))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Command numbers greather than 255. Example command 1280.
#
txdata = bytearray(1)
txdata[0] = 0
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 1280, txdata)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Broadcast Commands (eg. cmd 11, cmd 21)
#
txdata = bytearray(32) # i don't care data for this example.
CommunicationResult, SentPacket, RecvPacket = hart.PerformBroadcastTransaction(21, txdata)


#
# Kills all threads
#
hart.Stop()
