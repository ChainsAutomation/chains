# Physical Specifications:
## 1. Baud Rate:1200, 2400, 4800, 9600 (default), 19200, 38400, 57600
## 2. Data bits: 8
## 3. Parity: None
## 4. Stop Bit: 1
## 5. Flow Control: None
#
# Header, ID, Category, Page, Function, Length
#  ________________________________________________________________________________
# | MsgSize | Control | Data [0] | Data [1] | Data [2] | ... | Data [N] | Checksum |
# |_________|_________|__________|__________|__________|_____|__________|__________|
#


CMD_FIELDS = [
    "Header",
    "ID",
    "Category",
    "Page",
    "Function",
    "Length",
    "Size",
    "Control",
]


def print_response(bytearr):
    for index, val in enumerate(bytearr):
       print "response %d : %s" % (index, hex(val))

def print_cmd(bytearr):
    pass

def check_response(bytearr):
    resp_checksum = bytearr[-1]
    verify = checksum(bytearr[:-1])
    if not resp_checksum == verify:
        return False
    # TODO: Check response type, not just checksum
    return True

def checksum(bytearr):
    """  Takes an array of bytes and XOR's them  """
    cur = bytearr[0]
    for item in bytearr[1:]:
        cur = cur ^ item
    return cur

def prep_msg(cmd_arr):
    cmd_arr.insert(0, 0xA6) # Header
    cmd_arr.insert(1, 0x01) # Monitor ID: 0x01 -> 0xFF
    cmd_arr.insert(2, 0x00) # Category: Fixed @ 0x00
    cmd_arr.insert(3, 0x00) # Page: Fixed @ 0x00
    cmd_arr.insert(4, 0x00) # Function: Fixed @ 0x00
    cmd_arr.insert(5, 0) # length of array not including msgsize/header part
    cmd_arr.insert(6, 0x01) # Control: Fixed @ 0x01
    cmd_arr[5] = len(cmd_arr) - 5  # update length when done
    cmd_arr.append(checksum(cmd_arr)) # Checksum is all values XOR'ed except the checksum
    return cmd_arr


if __name__ == '__main__':
    import serial
    import sicp_codes_bdm.py
    import binascii
    # print sicp.CMD
    # command = prep_msg(bytearray([0x18, 0x01]))  # Power off
    command = prep_msg(bytearray([0x19]))  # Power status
    for index, val in enumerate(command):
       print "byte %d : %s" % (index, hex(val))
    # print command
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    ser.flushInput()
    ser.flushOutput()
    resp = bytearray([])
    ser.write(command)
    while True:
        for ch in ser.read():
            # print int(ch.encode('hex'),16)
            # print "So far: " + binascii.hexlify(resp)
            if len(resp) < 6:
                resp.append(ch)
            elif len(resp) < resp[4] + 4:  # Length field reached, total length not reached
                resp.append(ch)
            elif len(resp) == resp[4] + 4:  # End of response
                resp.append(ch)
                print "got complete response:" + binascii.hexlify(resp)
                print_response(resp)
                if check_response(resp):
                    print "Checksum works out"
                resp = bytearray([])
            else:
                resp = bytearray([])  # something went wrong, clearing
            #print "So far: " + binascii.hexlify(resp)
    ser.close()
