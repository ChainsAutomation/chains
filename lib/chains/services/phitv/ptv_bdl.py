############################################################
# MsgSize # Control # Data[0] # Data[1] ... [N] # Checksum #
############################################################
# 0x05    # 0x01    # 0xA2    # 0x00            # 0xA6     #
############################################################
# MsgSize: Size of full message including MsgSize itself.
#   => 1 (MsgSize) + 1 (Control)  + len(data) + 1 (checksum)
# Control: The number of the display, 0 for broadcast to all
#
#
#
#

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
    import sicp_codes_bdl
    for index, val in enumerate(prep_msg([0x01, 0xa2, 0x00])):
        print "byte %d : %s" % (index, hex(val))

