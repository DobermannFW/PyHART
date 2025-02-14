#
# Sometimes, for testing purpose you need to change address, delimiter
# and other field of the HART frame, send a frame splitted in two parts to test byte gap,
# send a wrong crc and so on...
# Here is shown how to do this.
#

import sys

#
# adjust this path base on script location
#
sys.path.append('../')

from PyHART.COMMUNICATION.CommCore import *
from PyHART.COMMUNICATION.Types import *
from PyHART.COMMUNICATION.Utils import *
from PyHART.COMMUNICATION.Device import *
from PyHART.COMMUNICATION.Packet import *
from PyHART.COMMUNICATION.Common import *


#
# Procedure to list communication ports and polling device (see example file 01)
#
count, listOfComPorts = ListCOMPort(additionalOptions=['Quit'])
comport = None
selection = 0
while (comport == None) and (selection != (count + 1)):
    print ('\nSelect the communication port.') 
    choice = input('Insert the number related to your choice and press enter: ')
    try:
        selection = int(choice)
    except:
        selection = 0
        
    print('') # new line
    
    if (selection == (count + 1)):
        print('Leaving application...')
        sys.exit()
    
    comport = GetCOMPort(selection, listOfComPorts)

hart = HartMaster(comport, \
                  MASTER_TYPE.PRIMARY, \
                  num_retry = 2, \
                  retriesOnPolling = False, \
                  autoPrintTransactions = True, \
                  whereToPrint = WhereToPrint.BOTH, \
                  logFile = 'terminalLog.log')

hart.Start()

FoundDevice = None
pollAddress = 0
EndPollingAddress = 3

while (FoundDevice == None) and (pollAddress <= EndPollingAddress):
    CommunicationResult, SentPacket, RecvPacket, FoundDevice = hart.LetKnowDevice(pollAddress)
    pollAddress += 1

if (FoundDevice is not None):
    PrintDevice(FoundDevice, hart)
else:
    print ('Device not found. Leaving Application...')
    hart.Stop()
    sys.exit()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# In this example I send a command zero with short address and polling address 
# equals to zero.
#
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82])
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)


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
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)


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
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Send command zero with wrong checksum byte
#
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x56])
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Send two consecutive command zero.
#
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82])
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# There are two additional parameters to this function.
# waitForRes: immagine you want to send a frame with a gap between bytes as in next example.
#             first piece of buffer won't wait for timeout
# closeRTS:   RTS is always set before to send, here it is possible to indicate if you want to reset RTS
#             after sending a message.
#

# Next message is  acommand 3 with 5 additional data byte. buffrer is divided in two separated buffers
txFrame1 = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x82, 0x9A, 0x84, 0x00, 0x00])
txFrame2 = bytearray([0x00, 0x03, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x9A])
# False, False means "do not wait for response" and "Do not close rts"
# In this way it seems that the message has been sent with a gap between two bytes
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame1, False, False)
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame2)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# send random data
# do not wait for a response, you already know that device will not respond to next message.
# close RTS at the end of message.
#
txFrame = bytearray([0x45, 0xFF, 0x02, 0x88, 0x45, 0xFF, 0x02, 0x88, 0x45, 0xFF, 0x02, 0x88, 0x45, 0xFF, 0x02, 0x88])
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame, False, True)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# NB
# When you try to send a custom frame using secondary master remember to change master type
# if you didn't set it in the constructor if you want to receive response.
# If you don't change master type, you will see in the log that device reponds but pyhart don't receive 
# response message, CommunicationResult will be equal to CommResult.NoResponse
#
hart.masterType = MASTER_TYPE.SECONDARY
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x00, 0x00, 0x00, 0x02]) # cmd 0 secondary master
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)
if (RecvPacket != None) and (CommunicationResult == CommResult.Ok):
    print('OK\n')
else:
    print('FAIL\n')
    
hart.masterType = MASTER_TYPE.PRIMARY    
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82]) # cmd 0 primary master
CommunicationResult, RecvPacket = hart.SendCustomFrame(txFrame)
if (RecvPacket != None) and (CommunicationResult == CommResult.Ok):
    print('OK\n')
else:
    print('FAIL\n')

#
# Kills all threads
#
hart.Stop()
