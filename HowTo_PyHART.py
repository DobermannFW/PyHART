###############################################################################
###############################################################################
##
## PyHART - Rev 3.3
##
## HOWTO MODULE
##
## The Purpose of this module is to teach how to use PyHART
##
## PyHART is OS indipendent
## You need python 3.6 o higher revision
## Use pip to install missing libraries (pySerial and others)
## Edit this file as UTF-8
##
###############################################################################
###############################################################################


"""
###############################################################################
1) IMPORT SECTION
"""
import sys
sys.path.append('./COMMUNICATION') # INDICATE THE PATH OF THE FOLDER COMMUNICATION

import time # used by a "sleep" in the following code ...

import Comm     # MANDATORY - module within the folder communication.
import CommCore # MANDATORY - module within the folder communication.
"""
only if using the encode/decode functions of the hart - modulo types within the folder communication. this module contains functions to easily transform received or sent data into bytearray or vice versa. all hart types are managed: int (1, 2, 3, 4 bytes), float, packAscii, date, time, ...
"""
import Types    # OPTIONAL - If you need to encode/decode bytes sent/received to/from HART data types.
                #            All HART types are supported (int, float, date, time, etc...)
                
import Utils    # OPTIONAL - This module contains a set of useful functions. A lot of them are used in the next code.
                
import Device   # OPTIONAL - This module handle a Device structure, for example Manufacturer Id, device type and so on.

import Packet   # OPTIONAL - This module contains the structure of HART PDU: preambles, delimiter, address, command, data lenght, data and checksum and a lot of fucntions.

# Print PyHART revision
# in the next will be explained how PyHART manages logging.
print("\nPyHART revision " + Utils.PyHART_Revision() + "\n")


# List available communication ports.
# this procedure allow the user to select a communication port.
count, listOfComPorts = Utils.ListCOMPort(True) # True or False to add "Quit" choice to the ports list.
comport = None
selection = 0
while (comport == None) and (selection != (count + 1)):
    print ("\nSelect the communication port. Insert related number and press enter.")
    try:
        selection = int(input())
    except:
        selection = 0
    
    # If Quit is selected...
    if (selection == (count + 1)):
        print("Leaving application...")
        sys.exit()
    
    comport = Utils.GetCOMPort(selection, listOfComPorts)


"""
###############################################################################
2) HOW TO INSTANTIATE HART COMMUNICATION OBJECT
   
   Class "HartMaster"
   
   MANDATORY PARAMETERS
   - port: communication port COM o TTY: string format
   
   PROTOCOL PARAMETERS
   - masterType: if you want to simulate a primary or a secondary master.
                 (CommCore.MASTER_TYPE.PRIMARY, CommCore.MASTER_TYPE.SECONDARY - If omitted, primary is the default)
   - num_retry: Number of retries in case of failure (If omitted, 3 is the default. It means 1 attemp + 3 retries) 
                If you don't want retries set it to zero. 3 is the default and the maximum allowed value.
   - retriesOnPolling: It means if retries have to be used also on command zero with short address. It is common to poll on more poll addresses
                       and it could be useful to not have retries in this case. Can be True, false or Omitted ( = True).
   
   LOG PARAMETERS
   - autoPrintTransactions: It is possible tochoose if to log automatically all transactions (question and response). (Omitted == True).
   - whereToPrint: Choose if PyHART has to log on terminal, on a file or both (WhereToPrint.BOTH, WhereToPrint.FILE, WhereToPrint.TERMINAL) (Omitted == TERMINAL)
   - logFile: the name of the file when "whereToPrint" is BOTH or FILE. If a file name is specified but "whereToPrint" is set to TERMINAL, 
              file is ignored. The file is opened in "append mode". Each session is identified by a timestamp.
   
   SYSTEM PARAMETERS
   - rt_os: (True o False) it means if PyHART is running on real time operating system. (Omitted == False)
            For example i tested PyHART on a Raspberry Pi3 with an OS with recompiled real-time kernel. 
            This parameter works combined with the next parameter.
            It is used to close RTS signal as soon as last byte is transmitted.
   - manageRtsCts: (True o False) indicates if PyHART has to manage RTS/CTS signals. It is useless with a modem that manages RTS by himself. (Omitted == False)
"""
hart = Comm.HartMaster(comport, CommCore.MASTER_TYPE.PRIMARY, num_retry = 0, retriesOnPolling = False, autoPrintTransactions = True, whereToPrint = Comm.WhereToPrint.BOTH, logFile = "terminalLog.log", rt_os = None, manageRtsCts = None)


"""
###############################################################################
3) START
   Start is mandatory. It opnes the port and starts network monitor thread.
"""
hart.Start()


"""
###############################################################################
3) POLLING
   This function run command zero with short address.
   The only parameter is the polling address.
   In the next example is performed a polling sequence fro poll address zero to 4.
"""
FoundDevice = None
pollAddress = 0

# polling from 0 to 4
while (FoundDevice == None) and (pollAddress < 5):
    # All transactions are logged in terminal and file since autoPrintTransactions = True.
    # It is not necessary to directly call logging functions.
    CommunicationResult, SentPacket, RecvPacket, FoundDevice = hart.LetKnowDevice(pollAddress)
    pollAddress += 1

if (FoundDevice is not None):
    # utility to log device data.
    # Also this will produce a log.
    Utils.PrintDevice(FoundDevice, hart)


"""
###############################################################################
4) UNDERSTAND RETURN VALUES OF THE FUNCTIONS THAT PERFORM HART COMMANDS
# Previous function ran comando zero and return values are CommunicationResult, SentPacket, RecvPacket e FoundDevice
#
# CommunicationResult: outcome of the communication
#              -Ok: Communication was Ok (regardless of response code whether it is zero or not)
#      -NoResponse: The master didn't receive a response (after a timeout).
#   -ChecksumError: The master calculated a checksum different from the checksum in the received frame.
#      -FrameError: received frame is inconsistent.
#            -Sync: Received bytes are discarded by the master untill it recognize a valid preambles sequence.
#
# SentPacket and RecvPacket: frames sent and received during a transaction.
#   Packets are classes defined in Packet module.
#   Packed attributes are preambles, delimiter, address, command, dataLen, 
#   resCode, device status, data e checksum.
#   In a sent packet, response code and device status don't have a meaning.
#
# FoundDevice: this is returned only by the function "LetKnowDevice(poll-address)".
#   If you want to communicate with more than one device, each time you recognize a device with "LetKnowDevice", it is possible to call 
#   the function "hart.SetOnlineDevice(device)" to change device without execute command zero again.
#   "hart.OnlineDevice()" gets current device.
#
"""
# Check communication result and response code
if (CommunicationResult == CommCore.CommResult.Ok) and (RecvPacket.resCode == 0):
    print("ok!")


"""
###############################################################################
5) TWO WAYS TO RUN HART COMMANDS
   - class method
   - utility in Utils module
"""
## EXAMPLE 01 - class method
# In this example is sent a command 15.
CommunicationResult, SentPacket, RecvPacket = hart.PerformTransaction(15, None) # None since command 15 doesn't requires data to be sent.
if (CommunicationResult == CommCore.CommResult.Ok):
    if (RecvPacket.resCode == 0):
        # Sent and Received packets are logged automatically (if in the constructor autoPrintTransactions = True)
        # Retrive some received data using functions in Type module
        URV = Types.BytearrayToFloat(RecvPacket.data[3:7])
        LRV = Types.BytearrayToFloat(RecvPacket.data[7:11])
        Unit = RecvPacket.data[2]
        
        print("read URV: {0}, read LRV: {1}".format(URV, LRV))
        print("read Unit: " + Utils.GetUnitString(Unit) + "\n")
    else:
        print("command 15 wrong response code: {0}".format(RecvPacket.resCode))
else:
    # Useful function to get a message related to a communication error
    print(Utils.GetCommErrorString(CommunicationResult) + "\n")

## EXAMPLE 02 - HART command using an utility
# There is an utility to incorporate the managing of command result and response code check. 
# The same of before cam be done in the next way.
# An additional parameter is returned: "retStatus".
# I don't need to print anything if command result or response code are not good. It is done by the function.
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 15, None)
if (retStatus == True):
    URV = Types.BytearrayToFloat(RecvPacket.data[3:7])
    LRV = Types.BytearrayToFloat(RecvPacket.data[7:11])
    Unit = RecvPacket.data[2]        
    print("read URV: {0}, read LRV: {1}".format(URV, LRV))
    print("read Unit: " + Utils.GetUnitString(Unit) + "\n")

# Similary to Utils.PrintDevice(FoundDevice, hart),
# there is the possibility to print a packet using Utils.PrintPacket(packet, hart).
# This is useful when autoPrintTransactions is set to False and we need to log only a particular packet between a lot of transaction.
# To test this function put autoPrintTransactions to false for a while and we restore it at the end of the demo.
hart.autoPrintTransactions = False

# Send HART command 1 and log it using PrintPacket function.
print ("\n::::::::::::::::::::::::::::: COMANDO 1 :::::::::::::::::::::::::::::")
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 1, None)
if (retStatus == True):
    print("---------------- TRANSMITTED ----------------")
    Utils.PrintPacket(SentPacket, hart)
    print("---------------- RECEIVED ----------------")
    Utils.PrintPacket(RecvPacket, hart)

# restore auto print before to continue this HowTo.
hart.autoPrintTransactions = True

"""
###############################################################################
6) EXAMPLES WITH OTHER COMMANDS AND UTILITIES AND TYPES MANAGEMENT
   - command with data to send.
   - Transmitted and received data are always bytearray.
"""
# Here send a command 35 and manage floating points and measurement unit
txdata = bytearray(9)
txdata[0] = Utils.GetUnitCode("Kilopascal") # Measurement units are listed in Utils module
txdata[1:] = Types.FloatToBytearray(120.43)
txdata[5:] = Types.FloatToBytearray(-120.43)
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 35, txdata)
if (retStatus == True):
    print("CALIBRATION DONE\n")

# Command 18, encode tag (Packed Ascii) and date
txdata = bytearray(21)
txdata[0:] = Types.PackAscii("NEW TAG")
txdata[6:] = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
txdata[18:] = Types.DateStringToBytearray("05/11/2016")
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 18, txdata)
if (retStatus == True):
    # Command 13 decode tag and data
    retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 13, None)
    if (retStatus == True):
        tag = Types.UnpackAscii(RecvPacket.data[0:6])
        date = Types.BytearrayToDateString(RecvPacket.data[18:21])                
        print("read tag: [{0}], read date: [{1}]\n".format(tag, date))


"""
###############################################################################
7) COMMANDS LARGER THAN 255
"""
# Command 1280
txData = bytearray(1)
txData[0] = 0
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 1280, txData)
print("See log...")


"""
###############################################################################
8) SEND BROADCAST FRAMES
"""
# Some commands as 11 or 21, can be sent with broadcast address.
# WARNING! In this case is not possible to use "Utils.HartCommand".

txdata = bytearray(32) # i don't care data for this example.
CommunicationResult, SentPacket, RecvPacket = hart.PerformBroadcastTransaction(21, txdata)

"""
###############################################################################
9) SEND CUSTOM FRAMES.
    Sometimes, for testing purposes, it is useful to works on frame bytes.
    If you want to change address, checksum, data lenght, delimiter or send casual sequences of bytes.
"""
# In this example I send a command zero with short address and polling address zero.
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82])
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)

# It is possible to use the class Packet
pkt = Packet.HartPacket()
pkt.preamblesCnt = 8
pkt.delimiter = 0x82
pkt.address = bytearray([0x80, 0x00, 0x00, 0x00, 0x00]) # Broadcast address
pkt.command = 21
pkt.dataLen = 32
pkt.resCode = 0
pkt.devStatus = 0
pkt.data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
pkt.checksum = pkt.ComputeChecksum() # Checksum computation

# Before to send the packet I have to transform it in bytearray.
txFrame = pkt.ToFrame()
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)

# Also here I use Packet class.
# I can use the address storewd in OnlineDevice.
pkt = Packet.HartPacket()
pkt.preamblesCnt = 8
pkt.delimiter = 0x82
if (hart is not None) and (hart.OnlineDevice() is not None): 
    pkt.address = hart.OnlineDevice().longAddress[:] # not broadcast as in the previous example but current device address.
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

"""
###############################################################################
10) STOP
    Stop() closes the communication port and terminates network monitor thread.
    After Stop(), it is possible to call Start() again without create a new communication object.
"""
hart.Stop()


"""
###############################################################################
11) NETWORK SNIFFER
    If you connect an additional HART modem PyHART can sniff the network.
    Example 1:
    Put field device in burst mode.
    Example 2:
    Log communication form primary or secondary master with a device
"""

# This is commented because there is a infinite cycle inside
"""
# Start monitoring again
hart.Start()

# CTRL+C is a bad way to kill a python script.
print("Press CTRL+C to exit.")

print("\nListening Network...")
# during this infinite cycle all transactions are logged
while True:
    time.sleep(0.250) # let time, probably also "pass" instead sleep is good.

hart.Stop()
"""


