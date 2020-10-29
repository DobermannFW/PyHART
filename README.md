# PyHART
PyHART is a set of Python modules that allow you to communicate through the HART protocol.

The strength of PyHART is that all the code is written in python.
This doesn't limit you to execute only one single command in a stand alone application.
You can use PyHART for testing or to write recipes that perform 
complex operations on a field device: calibration, configurations, etc...

PyHART simulates an HART master without manage the timing of a real master hart. 
It can't handle syncronism between primary and secondary masters and bursting slaves but it can be
a good sniffer of the network.

To better understand how PyHART works and how to use PyHART read the documentation
and take a look at the file HowTo_PyHART.py


# Future Improvements
1) Implementation of a datalink layer according with HART state machine for real-time systems.
   I tried to re-compile Kernel linux on Raspberry Pi board in real-time, I tried also low-latency Kernels.
   They works. Now I have to add the HART state machine to PyHART.
