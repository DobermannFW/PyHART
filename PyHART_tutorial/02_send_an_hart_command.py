#
# In this module is shown how to send a command to an HART device.
# Encode/decode data, logging and manage responses codes.
# 


import sys

#
# adjust this path base on script location
#
sys.path.append('../')

#
# Standard import.
#
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
    # globalPrintActivityLock avoids unwanted interruption of a text block.
    # the use of globalPrintActivityLock provided by PyHART is strongly suggested
    # when there is a bursting device or while you are logging network
    # and you also want to print something from your script.
    # In case there is only PyHART and a slave device, it could be not used.
    # If autoPrintTransactions is set to True...
    # - HART packets are printed automatically when a command is sent
    # - if WhereToPrint is BOTH, HART transactions and next print() are printed in terminal and in logfile
    # - if WhereToPrint is TERMINAL, HART transactions and next print() are printed only in terminal
    # - if WhereToPrint is FILE, HART transactions and next print() are printed only in log file and nothing will appear on the terminal
    # - if WhereToPrint is None, next print will appear on the terminal,
    #   sys.stdout is not changed by PyHART (this last case is useful if you have multiple instances of PyHART running, sys.stdout is not handled by a single module).
    with globalPrintActivityLock: 
        print('URV: {0}'.format(URV))
        print('LRV: {0}'.format(LRV))
        print('Unit: ' + GetUnitString(Unit) + '\n')
        print(GetCommErrorString(CommunicationResult) + '\n')
    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# The same of previous with logging disabled
# autoPrintTransactions can be enabled/disabled during script execution.
# HART transaction will not logged, only print in the script will be logged.
#
hart.autoPrintTransactions = False

retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 15, None)
if (retStatus == True):
    URV = BytearrayToFloat(RecvPacket.data[3:7])
    LRV = BytearrayToFloat(RecvPacket.data[7:11])
    Unit = RecvPacket.data[2] 
    # I don't use globalPrintActivityLock here:
    print('URV: {0}'.format(URV))
    print('LRV: {0}'.format(LRV))
    print('Unit: ' + GetUnitString(Unit) + '\n')
    print(GetCommErrorString(CommunicationResult) + '\n')

hart.autoPrintTransactions = True


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Usually a command is performed using the function HartCommand but it is possible to 
# use hart.PerformTransaction.
# HartCommand automatically prints errors (if there an error happen) and check if
# response code is OK or not.
# Using hart.PerformTransaction you have to do these checks manually.
#
CommunicationResult, SentPacket, RecvPacket = hart.PerformTransaction(15, None)
if CommunicationResult == CommResult.Ok:
    if RecvPacket.resCode == 0:
        print('Command 15 OK\n')
    else:
        print('Command 15 Err\n')
else:
    print(GetCommErrorString(CommunicationResult) + '\n')


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# In case logging is disabled but you want to print a particular transaction...
#
hart.autoPrintTransactions = False

retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 1, None)
if (retStatus == True):
    print('---------------- TRANSMITTED ----------------')
    # Functions provided by PyHART (PrintPacket, PrintDevice, etc...) never require the use of "globalPrintActivityLock"
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
        with globalPrintActivityLock:        
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
txdata = bytearray(32) # I don't care data for this example.
CommunicationResult, SentPacket, RecvPacket = hart.PerformBroadcastTransaction(21, txdata)


#
# Kills all threads
#

hart.Stop()
