#
# In this example the list of available communication port is shown.
# After the user selects a port a polling phase will start.
# As soon as a device is found, polling phase ends and 
# device identification data are shown.
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
# Procedure to list communication ports
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


#
# Instantiates and starts the communication object.
# Primary or Secondary Master (even if this is not a real master according to state machine timing, 
#                              packet format can change between Primary or secondary master).
# Num retry: 1 attemp + num of retry
# During polling phase you shoul not want retries to be faster. set retriesOnPolling = False.
# autoPrintTransactions = True means that all HART transactions will be logged automatically.
# If it is false, HART transactions will not be logged, only print() in user module will be printed.
# whereToPrint: where do you want to log? File, Terminal or Both?
# File name is ignored if whereToPrint is set to terminal.
# If whereToPrint is none, logging in file doesn't work at all, sys.stdout will be not changed.
# In next examples files will be shown more details about logging.
# timeout parameter is the time the master waits to receive a response. If master doesn't receive
# any response in this time it considers communication result as "no response received".
# Default (if omitted or None) is 3 seconds.
#
# Each parameter in the constructor can be changed at runtime accessing it directly.
# hart.TIME_OUT = 0.5
# hart.autoPrintTransactions = False
# and so on...
#
hart = HartMaster(comport, \
                  MASTER_TYPE.PRIMARY, \
                  num_retry = 2, \
                  retriesOnPolling = False, \
                  autoPrintTransactions = True, \
                  whereToPrint = WhereToPrint.BOTH, \
                  logFile = 'terminalLog.log',
                  timeout = None)


# PyHART needs to be started
hart.Start()


#
# Polling connected devices in range [0..EndPollingAddress] and 
# break and print identification data of the first device found.
#
FoundDevice = None
pollAddress = 0
EndPollingAddress = 2

#CommunicationResult, SentPacket, RecvPacket, FoundDevice = hart.LetKnowDevice(2)

while (FoundDevice == None) and (pollAddress <= EndPollingAddress):
    CommunicationResult, SentPacket, RecvPacket, FoundDevice = hart.LetKnowDevice(pollAddress)
    pollAddress += 1

if (FoundDevice is not None):
    PrintDevice(FoundDevice, hart)
else:
    print ('Device not found. Leaving Application...')
    hart.Stop() # remember to Stop
    sys.exit()


# Implements yor code here!


#
# Kills all threads
#
hart.Stop()

