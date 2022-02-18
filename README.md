# PyHART
PyHART is a set of Python modules that allow you to communicate through the HART protocol.

The strength of PyHART is that all the code is written in python.
This does not limit you to executing a single command in a stand alone application.
You can use PyHART for testing or to write recipes that perform 
complex operations on a field device: calibration, configurations, etc...

When PyHART is used on a PC, it simulates a HART master without to manage the timing of a real master state machine. It can’t handle syncronism between primary and secondary masters and bursting slaves but it is possible to perform point to point HART transactions and it can be a good sniffer of the network.
If PyHART is running on a real-time environment, it can be configured to work as a real HART master accordingly to HART specification data link. Pay attention, this feature has not been tested yet.  

To better understand how PyHART works and how to use PyHART check the examples in the PyHART_tutorial folder.

PyHART uses pySerial (https://pyserial.readthedocs.io/en/latest/index.html) to communicate via serial port.

