###############################################################################
###############################################################################
##
## PyHART - Master
##
###############################################################################
###############################################################################
import struct

"""
-------------------------------------------------------------------------------
SHORT/USHORT
-------------------------------------------------------------------------------
"""

#
# array to signed short
#
def BytearrayToShort(sintArray):
    return (struct.unpack(">h", sintArray))[0]

#
# signed short to array
#
def ShortToBytearray(sintNum):
    return bytearray(struct.pack(">h", sintNum))
    
#
# array to unsigned short
#
def BytearrayToUShort(uintArray):
    return (struct.unpack(">H", uintArray))[0]

#
# unsigned short to array
#
def UShortToBytearray(uintNum):
    return bytearray(struct.pack(">H", uintNum))


"""
-------------------------------------------------------------------------------
INT/UINT
-------------------------------------------------------------------------------
"""

#
# array to signed int
#
def BytearrayToSInt(sintArray):
    return (struct.unpack(">i", sintArray))[0]

#
# signed int to array
#
def SIntToBytearray(sintNum):
    return bytearray(struct.pack(">i", sintNum))

#
# array to unsigned int
#
def BytearrayToUInt(uintArray):
    return (struct.unpack(">I", uintArray))[0]

#
# unsigned int to array
#
def UIntToBytearray(uintNum):
    return bytearray(struct.pack(">I", uintNum))


"""
-------------------------------------------------------------------------------
FLOAT
-------------------------------------------------------------------------------
"""

#
# array to float
#
def BytearrayToFloat(floatArray):
    return (struct.unpack(">f", floatArray))[0]


#
# float to array
#
def FloatToBytearray(floatNum):
    return bytearray(struct.pack(">f", floatNum))


"""
-------------------------------------------------------------------------------
DATE/TIME
-------------------------------------------------------------------------------
"""

#
# array to date string
#
def BytearrayToDateString(dateArray):
    date = ["", "", ""]
    if (len(dateArray) >= 3):
        date[0] = "{0:02d}".format(dateArray[0])
        date[1] = "{0:02d}".format(dateArray[1])
        date[2] = "{0:04d}".format((dateArray[2] + 1900))
    return (date[0] + "/" + date[1] + "/" + date[2])

#
# date string to array
#
def DateStringToBytearray(dateString):
    return bytearray([int(dateString[:2]), int(dateString[3:5]), (int(dateString[6:]) - 1900)])

#
# array to Time
#   
def BytearrayToTimeString(timeArray):
    return "{0:f}".format((BytearrayToUInt(timeArray) * 0.03125))

#
# Time to array
#
def TimeStringToBytearray(timeString):
    return UIntToBytearray(int(float(timeString) / 0.03125))


"""
-------------------------------------------------------------------------------
PACKED ASCII
-------------------------------------------------------------------------------
"""

#
# Pack ASCII
#
def PackAscii(unpackedStr):
    unpackedStrLen = len(unpackedStr)
    unpackedString = bytearray(unpackedStr, "ascii")
    
    packedString = None
    packedBits = 6 * unpackedStrLen
    
    if (packedBits % 8) > 0:
        packedString = bytearray(int(packedBits / 8) + 1)
    else:
        packedString = bytearray(int(packedBits / 8))
    
    i = 0
    bit8 = 0
    j = 0
    while (i < unpackedStrLen):
        packedByte = unpackedString[i] & 63
        
        bit6 = 0
        while (bit6 < 6):
            val = 0
            if (packedByte & 0x20) > 0:
                val = 1
            packedByte <<= 1
            
            if (bit8 == 0):
                packedString[j] |= ((val << 7) & 0x80)
            elif (bit8 == 1):
                packedString[j] |= ((val << 6) & 0x40)
            elif (bit8 == 2):
                packedString[j] |= ((val << 5) & 0x20)
            elif (bit8 == 3):
                packedString[j] |= ((val << 4) & 0x10)
            elif (bit8 == 4):
                packedString[j] |= ((val << 3) & 0x08)
            elif (bit8 == 5):
                packedString[j] |= ((val << 2) & 0x04)
            elif (bit8 == 6):
                packedString[j] |= ((val << 1) & 0x02)
            elif (bit8 == 7):
                packedString[j] |= (val & 0x01)
            
            bit6 += 1
            bit8 += 1
            if (bit8 == 8):
                bit8 = 0
                j += 1
        
        i += 1
        
    return packedString

#
# Unpack ASCII
#    
def UnpackAscii(packedString):
    packedLen = len(packedString)
    unpackedLen = int((8 * packedLen) / 6)
    unpackedArray = bytearray(unpackedLen)

    packed_idx = 0
    bit_counter = 8
    curr_byte = 0

    for i in range(unpackedLen):

        for j in range(6):

            if bit_counter == 8:
                curr_byte = packedString[packed_idx]
                packed_idx += 1
                bit_counter = 0

            bit_counter += 1

            bit_val = 0
            if (curr_byte & 0x80):
                bit_val = 1
            curr_byte <<= 1
            
            if (j == 0):
                unpackedArray[i] |= ((bit_val << 5) & 0x20)
                v = 0
                if (bit_val == 0):
                    v = 1
                unpackedArray[i] |= ((v << 6) & 0x40)
            elif (j == 1):
                unpackedArray[i] |= ((bit_val << 4) & 0x10)
            elif (j == 2):
                unpackedArray[i] |= ((bit_val << 3) & 0x08)
            elif (j == 3):
                unpackedArray[i] |= ((bit_val << 2) & 0x04)
            elif (j == 4):
                unpackedArray[i] |= ((bit_val << 1) & 0x02)
            elif (j == 5):
                unpackedArray[i] |= (bit_val & 0x01)
    
    unpackedStr = unpackedArray.decode("ascii")
    return unpackedStr
