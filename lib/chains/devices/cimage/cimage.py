#!/usr/bin/python2

import time
import numpy as np
import cv2
import urllib2

def _read_image(path):
    """ Read image from filesystem or url, return local path if ok (?) """
    if path.startswith('http'):
        # TODO: download image and store? Read and discard?
        pass
    else:
        # expect image path to be a local file
        pass

if __name__ == '__main__':
    from pprint import pprint
    import sys
    import serial
    in_img = sys.argv[1]
    act = sys.argv[2]
    # cmds = sys.argv[3:]
    # for c in cmds:
    #     print "command : %s" % c
    #     time.sleep(0.5)
    img = cv2.imread(in_img,0)
