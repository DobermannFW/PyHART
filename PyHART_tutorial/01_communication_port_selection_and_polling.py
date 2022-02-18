#
# In this example a list of communication port is shown.
# After the user select a port a polling phase will start.
# As soon as a device is found, polling phase ends and 
# device identification data are shown.
# 


#
# Standard import. Append the path of PyHART. Since this file is in the folder PyHART_tutorial,
# just go back one folder.
#
import sys
sys.path.append('../')
from PyHART.COMMUNICATION.CommCore import HartMaster, WhereToPrint
from PyHART.COMMUNICATION.Utils import *
from PyHART.COMMUNICATION.System import *

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


#
# Kills all threads
#
hart.Stop()

