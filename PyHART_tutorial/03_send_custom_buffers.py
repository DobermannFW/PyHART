#
# Sometimes, for testing purpose you need to change address, delimiter
# and other field of the HART frame.
# Here is shown how to do this.
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
from PyHART.COMMUNICATION.Utils import *
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
# In this example I send a command zero with short address and polling address 
# equal to zero.
#
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82])
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# It is possible to use the 'Packet' class 
#
pkt = HartPacket()
pkt.preamblesCnt = 8
pkt.delimiter = 0x82
pkt.address = bytearray([0x80, 0x00, 0x00, 0x00, 0x00]) # Broadcast address
pkt.command = 21
pkt.dataLen = 32
pkt.resCode = 0
pkt.devStatus = 0
pkt.data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
pkt.checksum = pkt.ComputeChecksum() # Checksum computation
txFrame = pkt.ToFrame() # Before to send the packet I have to transform it in bytearray.
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Also here I use Packet class.
# I can use the address stored in OnlineDevice (if a command zero has been sent before).
#
pkt = HartPacket()
pkt.preamblesCnt = 8
pkt.delimiter = 0x82
if (hart is not None) and (hart.OnlineDevice is not None): 
    pkt.address = hart.OnlineDevice.longAddress[:] # not broadcast as in the previous example but current device address.
else:
    pkt.address = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
pkt.command = 21
pkt.dataLen = 32
pkt.resCode = 0
pkt.devStatus = 0
pkt.data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
pkt.checksum = pkt.ComputeChecksum()

txFrame = pkt.ToFrame()
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)


#
# Kills all threads
#
hart.Stop()
