# Physical Specifications
# 1. Baud Rate:1200, 2400, 4800, 9600 (default), 19200, 38400, 57600
# 2. Data bits: 8
# 3. Parity: None
# 4. Stop Bit: 1
# 5. Flow Control: None

#  ________________________________________________________________________________
# | MsgSize | Control | Data [0] | Data [1] | Data [2] | ... | Data [N] | Checksum |
# |_________|_________|__________|__________|__________|_____|__________|__________|
#

import serial

ser = serial.Serial(
    port='COM1',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

def checksum(bytearr):
    """  Takes an array of bytes and XOR's them  """
    cur = bytearr[0]
    for item in bytearr[1:]:
        cur = cur ^ item
    return cur

def prep_msg(cmd_arr):
    cmd_arr.insert(0, len(cmd_arr) + 2)
    cmd_arr.append(checksum(cmd_arr))
    return cmd_arr


if __name__ == '__main__':
    for index, val in enumerate(prep_msg([0x01, 0xa2, 0x00])):
        print "byte %d : %s" % (index, hex(val))

