#!/usr/bin/env python
import sys, os
from chains.common import config, log, utils

class Daemon:

    def __init__(self, daemonType, daemonId, callback):
        self.logFile = config.getLogFile(daemonType) #, daemonId)
        self.pidFile = config.getPidFile(daemonType) #, daemonId)
        self.name = 'chains-%s-%s' % (daemonType, daemonId)
        self.daemonType = daemonType
        self.daemonId = daemonId
        self.callback = callback

    def main(self):
        self.callback(self.daemonId)

    def fork(self):

        if os.path.exists(self.pidFile):
            with open(self.pidFile, 'r') as f:
                pid = int(f.read())
            # @todo: is this a good way to check if process is alive?
            try:
                os.getpgid(pid)
                print "Already running at PID %s" % pid
                sys.exit(1)
            except OSError, e:
                if e.args[0] == 3: # process not found
                    os.remove(self.pidFile)
                else:
                    raise

        # do the UNIX double-fork magic, see Stevens' "Advanced 
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1)
        # decouple from parent environment
        os.chdir('/') # don't prevent unmounting
        os.setsid() 
        os.umask(0) 
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent, print eventual PID before
                pf = open(self.pidFile, 'w')
                pf.write("%d"%pid)
                pf.close()
                sys.exit(0) 
        except OSError, e: 
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1) 
    
        # start the daemon main loop
        #sys.stdout = sys.stderr = log.OutputLog(open(self.logFile, 'a+'))
        self.main()

def getDaemonMainFunction(daemonType):
    if daemonType == 'manager':
        import chains.manager
        return chains.manager.main
    if daemonType == 'orchestrator':
        import chains.orchestrator
        return chains.orchestrator.main
    if daemonType == 'reactor':
        import chains.reactor
        return chains.reactor.main
    raise Exception('Unknown daemon type: %s' % daemonType)

def resolveDaemonId(value):
    hostname = utils.getHostName()
    return value.replace('{hostname}', hostname)

def main(daemonType, fork=True):
    conf = config.data(daemonType)
    conf['id'] = resolveDaemonId(conf['id'])
    if not conf:
        raise Exception('No section "daemon_%s" in config' % id)
    for k in conf:
        if k[0:4] == 'env_':
            log.info('Set ENV.%s = %s' % (k[4:],conf[k]))
            os.environ[k[4:]] = conf[k]
    d = Daemon(daemonType, conf['id'], getDaemonMainFunction(daemonType))
    if fork:
        d.fork()
    else:
        d.main()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'usage: daemon.py <daemon-type> [fork]'
        sys.exit(1)
    fork = False
    if len(sys.argv) > 2 and sys.argv[2] != '0':
        fork = True
    main(sys.argv[1], fork)
