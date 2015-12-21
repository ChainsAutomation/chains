#!/usr/bin/env python
import sys
from . import Daemon, getDaemonMainFunction, resolveDaemonId, main

if len(sys.argv) < 2:
    print 'usage: daemon.py <daemon-type> [fork]'
    sys.exit(1)
fork = False
if len(sys.argv) > 2 and sys.argv[2] != '0':
    fork = True
main(sys.argv[1], fork)
