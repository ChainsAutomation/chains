#!/usr/bin/python2

import time
from collections import OrderedDict
import serial

try:
    # Importing when used as a module
    from . import benq_codes
except:
    # Importing when used as a cli program
    import benq_codes

def check_cmd(cmd, param):
    if cmd in benq_codes.CODES:
        return True
    else:
        # undefined type
        return False

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
        print "Writing: " + c + "\\r\\n"
        ser.write("!1" + c + '\r\n')
        ret_val = ser.readline()
        print "\'" + ret_val + "\'"
        # time.sleep(0.5)
    ser.close()
