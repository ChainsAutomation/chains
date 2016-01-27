#!/usr/bin/python2

#CMDS[topic_index]: a topic array
#CMDS[topic_index][0] : topic name (PWR)
#CMDS[topic_index][1] : topic description
#CMDS[topic_index][2] : all commands array
#CMDS[topic_index][2][cmd_index] : command array
#CMDS[topic_index][2][cmd_index][0] : command name
#CMDS[topic_index][2][cmd_index][1] : command description
#CMDS[topic_index][2][cmd_index][2] : command type dict
#CMDS[topic_index][2][cmd_index][3] : command models support
#CMDS[topic_index][2][cmd_index][3][model_index] : model support

# import time
from collections import OrderedDict
try:
    # Importing when used as a module
    from . import iscp_codes
except:
    # Importing when used as a cli program
    import iscp_codes


def model_cmds(model):
    topic_desc = OrderedDict()
    m_cmds = OrderedDict()
    for index, group in enumerate(iscp_codes.MODELS):
        if model in group:
            mindex = index
            break
    # topics = iscp_codes.CMDS
    # for topic in topics:
    for topic in iscp_codes.CMDS:
        topic_desc.update({topic[0]: topic[1]})
        if topic[0] not in m_cmds:
            # Keep subcommands ordered:
            m_cmds.update({topic[0]: OrderedDict()})
        for cmd in topic[2]:
            if cmd[3][mindex]:  # Model is supported
                m_cmds[topic[0]].update({cmd[0]: {'description': cmd[1], 'type': cmd[2]}})
        if not m_cmds[topic[0]]:
            # print "Empty topic: %s" % topic[0]
            del m_cmds[topic[0]]
        else:
            # print "Supported topic: %s" % topic[0]
            pass
    return (topic_desc, m_cmds)


def check_cmd(cmd, param, ctype):
    # TODO: prefix, hex-type hex(myint)[2:].upper()
    prefix = ''
    if 'prefix' in ctype:
        prefix = ctype['prefix']
    if ctype['type'] == 'range':
        param = int(param)
        if not ctype['min'] <= param <= ctype['max']:
            return False
        else:
            neg = False
            if param < 0:
                neg = True
                param = abs(param)
            # convert to hex without 0x if data is hex
            if ctype['data'] == 'hex':
                param = hex(param)[2:].upper()
            if 'pad' in ctype:
                param = str(param).zfill(ctype['pad'])
            # Default unsigned, padded range:
            if 'rtype' not in ctype:
                return cmd + prefix + param
            if ctype['rtype'] == 'signed':
                if param == "0":
                    return cmd + prefix + '00'
                elif neg:
                    return cmd + prefix + '-' + param
                else:
                    return cmd + prefix + '+' + param
            else:
                return False
    elif ctype['type'] == 'string':
        if not ctype['min'] <= len(param) <= ctype['max']:
            return False
        else:
            return cmd + prefix + str(param)
    elif ctype['type'] == 'noarg':
        return cmd
    else:
        # undefined type
        return False

if __name__ == '__main__':
    from pprint import pprint
    import sys
    import serial
    topic_desc, cmds = model_cmds('TX-SR705')
    # pprint(cmds)
    for cmd in cmds:
        print cmd + ' : ' + topic_desc[cmd]
        for subcmd in cmds[cmd]:
            print '\t' + subcmd + ': ' + cmds[cmd][subcmd]['description']
            if cmds[cmd][subcmd]['type']:
                pprint(cmds[cmd][subcmd]['type'], indent=12)
    # pprint(cmds['PWR'])
    ser_dev = sys.argv[1]
    do_cmds = sys.argv[2:]
    ser = serial.Serial(port=ser_dev,
                        baudrate=9600,
                        timeout=0.05,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        )
    for c in do_cmds:
        print "Writing: !1" + c + "\\r\\n"
        ser.write("!1" + c + '\r\n')
        ret_val = ser.readline()
        print "\'" + ret_val + "\'"
        # time.sleep(0.5)
    ser.close()
