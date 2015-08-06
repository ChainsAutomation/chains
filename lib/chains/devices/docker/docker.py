# -*- coding: utf-8 -*-
import socket
import json
import time

def pretty(jobj):
    print json.dumps(jobj, sort_keys=True, indent=4, separators=(',', ': '))


