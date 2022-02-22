#
# It is possible to log HART transactions.
# For example log a bursting device or log transactions with other masters
# by connecting a second HART modem.
#


#
# Standard import. Append the path of PyHART. Since this file is in the folder PyHART_tutorial,
# just go back one folder.
#
import sys
sys.path.append('../')
from PyHART.COMMUNICATION.CommCore import *
from PyHART.COMMUNICATION.Utils import *
from PyHART.COMMUNICATION.Common import *
from time import sleep


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
# Here it is very important to define a log file and ensure that 
# 'autoPrintTransactions' is set to 'True' and that 'whereToPrint' is set 
# to 'CommCore.WhereToPrint.BOTH' (Terminal and file) or 
# 'CommCore.WhereToPrint.FILE' (log only in the log file).
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

while True:
    sleep(5) # let time to other threads
    
    # @TODO
    # To interrupt this infinite cycle you have to implement a 'read keypress'
    # mechanism, for example if the user press enter break the cycle.


#
# Kills all threads
#
hart.Stop()

