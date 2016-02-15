#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function

import os
import sys

if len(sys.argv) < 2 or sys.argv[1] not in ['master', 'slave']:
    sys.exit("Usage: %s <master|slave>" % sys.argv[0])

if sys.argv[1] == 'master':
    tpath = 'MasterImages'
elif sys.argv[1] == 'slave':
    tpath = 'SlaveImages'
else:
    sys.exit('Impossibru!')

arch = os.uname()[4]
if arch.startswith('x86'):
    archpath = 'X86'
elif arch.startswith('arm'):
    archpath = 'RPi'
else:
    print("Unknown architecture, exiting")
    sys.exit(1)
print("Architecture detected to be %s" % archpath)

if os.path.isdir('misc/Docker/'):
    stubdir = 'misc/Docker/'
elif os.path.isdir('../misc/Docker/'):
    stubdir = '../misc/Docker/'
elif os.path.isdir('/srv/chains/misc/Docker/'):
    stubdir = '/srv/chains/misc/Docker/'
else:
    sys.exit("Unable to detect chains location, please run this command from the chains root dir or keep chains in /srv/chains/")

fullpath = os.path.realpath('%s/%s/%s' % (stubdir, tpath, archpath))
print("full path to docker stubs for this image is %s" % fullpath)

chainsdir = os.path.realpath(stubdir + '../../')
print("chains install detected at %s" % chainsdir)

stubfiles = next(os.walk(fullpath))[2]
stubfiles.sort()
dockercontent = ''
for sfile in stubfiles:
    # print "found stub: %s" % sfile
    # print 'stubs real path: %s' % os.path.realpath(fullpath + '/' + os.readlink(fullpath + '/' + stubfiles[0]))
    with open(os.path.realpath(fullpath + '/' + os.readlink(fullpath + '/' + sfile)), 'r') as stub:
        tempcontent = stub.read()
        dockercontent = dockercontent + tempcontent

# print "Full dockerfile:"
# print dockercontent
with open(chainsdir + '/Dockerfile', 'w') as dockerfile:
    dockerfile.write(dockercontent)
    dockerfile.close()
    print("Dockerfile written to %s/Dockerfile" % chainsdir)
    print("Build docker image using the following command in the %s directory:" % chainsdir)
    print("sudo docker build --no-cache -t chains/chains-%s ." % sys.argv[1])

