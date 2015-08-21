'''
Process manager for services using subprocess
'''

from chains.common import config, log
from chains import service
import os, signal, time, subprocess, json, psutil, types

processes = {}

'''
todo:
 * capture stdout/stderr? --> no, do it in service-runner
 - option for relative path in config.command? then need servicedir config or something
 * move pidfile stuff here, so non-py devs does not have to do it themselves
 - some duplicate code here and in daemon/__init__.py - consolidate?
'''
def start(serviceConfig):

    serviceId = serviceConfig['main'].get('id')

    log.info('Start service: %s' % serviceId)

    pid      = isRunning(serviceId)

    if pid:
        log.error("Could not start service %s because already running on pid %s" % (serviceId, pid))
        return

    if serviceConfig.get('command'):
        command = serviceConfig.get('command')
    else:
        command = '%s/service/runservice.py' % config.get('libdir')

    command = [command, json.dumps(serviceConfig)]

    log.info('Start service command: %s' % (command,))

    # We need close_fds=True to avoid some crap being inherited from parent->child process,
    # which would cause manager process to not free all resources when killed, unless
    # all service subprocesses are also dead first, which we do not want to require.
    #proc = subprocess.Popen(command)
    processes[serviceId] = subprocess.Popen(command, close_fds=True)
    setPid(serviceId, processes[serviceId].pid)
    log.info("Started service %s on pid %s" % (serviceId, pid))

def stop(serviceId):

    # Only stop if already running
    pid = isRunning(serviceId)
    if not pid:
        log.info('Ignore stop service %s since not running' % serviceId)
        return

    # Two cases here:
    #
    #  1. Service subprocess was started by this process
    #  2. Service subprocess was started by another process (manager has been restarted)
    #
    #  In the case of 1, we should use the process object we have here,
    #  terminate() it, wait() for it, to ensure that its parent process (us) stops using it,
    #  or else it will wait for this and become a zombie.
    #
    #  In the case of 2, we don't have the process object since we didn't start it,
    #  but it won't have a parent process waiting for it either, so we can safely
    #  kill it using sinals only, and it should not become a zombie.
    #
    proc   = None
    logtxt = 'started by other process'
    if processes.has_key(serviceId):
        logtxt = 'started by this process'
        proc   = processes[serviceId]

    # Kill gracefully with SIGTERM first
    log.info('Stopping service %s (%s)' % (serviceId,logtxt))
    if proc:
        proc.terminate()
    else:
        os.kill(pid, signal.SIGTERM)

    for i in range(1,30):
        if proc:
            if proc.poll() != None:
                return
        else:
            if not isRunning(serviceId):
                return
        time.sleep(0.5)

    log.info('Kill service %s since still not stopped' % serviceId)
    if proc:
        proc.kill()
    else:
        os.kill(pid, signal.SIGKILL)
    
def isRunning(serviceId):

    # Check pidfile
    pid = getPid(serviceId)
    if not pid:
        log.info('Proc no pid: %s' % pid)
        return False    

    # Check if pid in pidfile actually exists
    try:
        os.kill(pid, 0)
    except OSError:
        log.info('Proc not running (kill -0): %s' % pid)
        delPid(serviceId)
        return False

    # Check if defunct/zombie process
    proc = psutil.Process(pid)
    status = None
    if type(proc.status) == types.FunctionType:
        status = proc.status()
    else:
        status = proc.status
    if status == psutil.STATUS_ZOMBIE:
        log.info('Proc not running (zombie): %s' % pid)
        delPid(serviceId)
        return False
        
    # Process is running
    log.info('Proc running with status %s: %s' % (status,pid))
    return pid

def getRunningServices():
    result = {}
    for path in os.listdir(config.get('rundir')):
        filename, extension = path.split('.')
        if extension != 'pid':
            continue
        parts = filename.split('-')
        if len(parts) < 2 or parts.pop(0) != 'service':
            continue
        serviceName = '-'.join(parts)
        pid = isRunning(serviceName)
        result[serviceName] = pid
    return result
        

def getPid(serviceId):
    pidFile = getPidFile(serviceId)
    if not os.path.exists(pidFile):
        return None
    with open(pidFile, 'r') as fp:
        pid = fp.read().strip()
    if pid:
        return int(pid)
    return None

def setPid(serviceId, pid):
    pidFile = getPidFile(serviceId)
    with open(pidFile, 'w') as fp:
        fp.write('%s' % pid)

def delPid(serviceId):
    pidFile = getPidFile(serviceId)
    if os.path.exists(pidFile):
        os.unlink(pidFile)

def getPidFile(serviceId):
    return '%s/service-%s.pid' % (config.get('rundir'), serviceId)

