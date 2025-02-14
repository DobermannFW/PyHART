#
# It is possible to log HART transactions.
# For example log a bursting device or log transactions with other masters
# by connecting a second HART modem.
#


#
# Standard import.
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
from time import sleep
import keyboard


#
# Variables and keyboard event to handle keypressed used to break infinite cycle
#
stop = False

def OnHotKey(event):
    global stop
    stop = True

keyboard.add_hotkey('ctrl+q', OnHotKey)


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


hart = HartMaster(comport, \
                  MASTER_TYPE.PRIMARY, \
                  num_retry = 2, \
                  retriesOnPolling = False, \
                  autoPrintTransactions = True, \
                  whereToPrint = WhereToPrint.BOTH, \
                  logFile = 'terminalLog.log')

hart.Start()

# All HART communications will be logged.
# Burst, Other master and slave communications...
# You need to have a parallel modem connection.

print('Press \'CTRL+Q\' to terminate operations')

while stop == False:
    sleep(0.250) # let time to other threads


# There is an infinite cycle so never reach here...
# Only to remember to call Stop() after using Start()
hart.Stop()

