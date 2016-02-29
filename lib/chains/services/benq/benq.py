from __future__ import absolute_import
from __future__ import print_function

### BENQ serial interface information
# Baud rate: 115200 (Default)
# Data length: 8 bits
# Parity: None
# Stop bit: 1 bit
# Flow control: None
#
###
# 
# 
# 
# 

import time
from collections import OrderedDict
import serial

from . import benq_codes

def check_cmd(cmd, param):
    if cmd in benq_codes.CODES:
        return True
    else:
        # undefined type
        return False

def power_on():
    pass

def power_off():
    pass

def v12_trigger():
    pass

def output_set():
    pass

def pip_set_output():
    pass

def pip_toggle():
    pass

if __name__ == '__main__':
    from pprint import pprint
    import sys
    import serial
    ser_dev = sys.argv[1]
    do_cmds = sys.argv[2:]
    ser = serial.Serial(port=ser_dev,
                        baudrate=115200,
                        timeout=0.05,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        )
    for c in do_cmds:
        print("Writing: " + c + "\\r\\n")
        ser.write("!1" + c + '\r\n')
        ret_val = ser.readline()
        print("\'" + ret_val + "\'")
        # time.sleep(0.5)
    ser.close()
