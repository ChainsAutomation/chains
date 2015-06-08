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

from collections import OrderedDict
try:
    from . import iscp_codes
except:
    import iscp_codes


def model_cmds(model):
    topic_desc = OrderedDict()
    m_cmds = OrderedDict()
    for index, group in enumerate(iscp_codes.MODELS):
        if model in group:
            mindex = index
            break
    topics = iscp_codes.CMDS
    for topic in topics:
        topic_desc.update({topic[0]: topic[1]})
        if topic[0] not in m_cmds:
            m_cmds.update({topic[0]: {}})
        for cmd in topic[2]:
            if cmd[3][mindex]:  # Model is supported
                m_cmds[topic[0]].update({cmd[0]: {'description': cmd[1], 'type': cmd[3]}})
        if not m_cmds[topic[0]]:
            # print "Empty topic: %s" % topic[0]
            del m_cmds[topic[0]]
        else:
            # print "Supported topic: %s" % topic[0]
            pass
    return (topic_desc, m_cmds)

if __name__ == '__main__':
    # from pprint import pprint
    import sys
    import serial
    topic_desc, cmds = model_cmds('TX-SR705')
    # pprint(cmds)
    for cmd in cmds:
        print cmd + ' : ' + topic_desc[cmd]
    # pprint(cmds['PWR'])
    ser_dev = sys.argv[1]
    do_cmds = sys.argv[2:]
    ser = serial.Serial(port=ser_dev,
                        baudrate=9600,
                        timeout=0,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        )
    for c in do_cmds:
        ser.write("!" + c + '\r\n')
        ret_val = ser.readline()
    ser.close()
