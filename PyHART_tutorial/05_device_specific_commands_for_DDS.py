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
from PyHART.COMMUNICATION.Common import *

#
# Procedure to list communication ports
#
count, listOfComPorts = ListCOMPort(True)
comport = None
selection = 0
while (comport == None) and (selection != (count + 1)):
    print('\nSelect the communication port.') 
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
# Command 240
#
# Send command 240 with slot 8
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 240, bytearray([8]))

# Send command 240 with slot 26
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 240, bytearray([26]))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Command 79 Simulation Enable
#
slot = 0 # Pressure
simulationEnable = 1 # enable
unit = GetUnitCode('Kilopascal')
status = 0

txdata = bytearray(8)
txdata[0] = slot
txdata[1] = simulationEnable
txdata[2] = unit
txdata[3:6] = FloatToBytearray(34.734)
txdata[7] = status

retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 79, txdata)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Command 79 Simulation Disable
#
txdata = bytearray([slot, not simulationEnable, unit, 0, 0, 0, 0, 0])
retStatus, CommunicationResult, SentPacket, RecvPacket = HartCommand(hart, 79, txdata)


#
# Kills all threads
#
hart.Stop()

