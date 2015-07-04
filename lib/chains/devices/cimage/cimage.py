#!/usr/bin/python2

import time
import numpy as np
import cv2

if __name__ == '__main__':
    from pprint import pprint
    import sys
    import serial
    act = sys.argv[1]
    img = sys.argv[2]
    # cmds = sys.argv[3:]
    # for c in cmds:
    #     print "command : %s" % c
    #     time.sleep(0.5)
