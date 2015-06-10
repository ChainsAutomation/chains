'''
Process manager for devices using subprocess
'''

from chains.common import config, log
from chains import device
import os, signal, time, subprocess, json, psutil, types

processes = {}

'''
todo:
 * capture stdout/stderr? --> no, do it in device-runner
 - option for relative path in config.command? then need devicedir config or something
 * move pidfile stuff here, so non-py devs does not have to do it themselves
 - some duplicate code here and in daemon/__init__.py - consolidate?
'''
def start(deviceConfig):

    deviceId = deviceConfig['main'].get('id')

    log.info('Start device: %s' % deviceId)

    pid      = isRunning(deviceId)

    if pid:
        log.error("Could not start device %s because already running on pid %s" % (deviceId, pid))
        return

    if deviceConfig.get('command'):
        command = deviceConfig.get('command')
    else:
        command = '%s/device/rundevice.py' % config.get('libdir')

    command = [command, json.dumps(deviceConfig)]

    log.info('Start device command: %s' % (command,))

    # We need close_fds=True to avoid some crap being inherited from parent->child process,
    # which would cause manager process to not free all resources when killed, unless
    # all device subprocesses are also dead first, which we do not want to require.
    #proc = subprocess.Popen(command)
    processes[deviceId] = subprocess.Popen(command, close_fds=True)
    setPid(deviceId, processes[deviceId].pid)
    log.info("Started device %s on pid %s" % (deviceId, pid))

def stop(deviceId):

    # Only stop if already running
    pid = isRunning(deviceId)
    if not pid:
        log.info('Ignore stop device %s since not running' % deviceId)
        return

    # Two cases here:
    #
    #  1. Device subprocess was started by this process
    #  2. Device subprocess was started by another process (manager has been restarted)
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
    if processes.has_key(deviceId):
        logtxt = 'started by this process'
        proc   = processes[deviceId]

    # Kill gracefully with SIGTERM first
    log.info('Stopping device %s (%s)' % (deviceId,logtxt))
    if proc:
        proc.terminate()
    else:
        os.kill(pid, signal.SIGTERM)

    for i in range(1,30):
        if proc:
            if proc.poll() != None:
                return
        else:
            if not isRunning(deviceId):
                return
        time.sleep(0.5)

    log.info('Kill device %s since still not stopped' % deviceId)
    if proc:
        proc.kill()
    else:
        os.kill(pid, signal.SIGKILL)
    
def isRunning(deviceId):

    # Check pidfile
    pid = getPid(deviceId)
    if not pid:
        log.info('Proc no pid: %s' % pid)
        return False    

    # Check if pid in pidfile actually exists
    try:
        os.kill(pid, 0)
    except OSError:
        log.info('Proc not running (kill -0): %s' % pid)
        delPid(deviceId)
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
        delPid(deviceId)
        return False
        
    # Process is running
    log.info('Proc running with status %s: %s' % (status,pid))
    return pid

def getRunningDevices():
    result = {}
    for path in os.listdir(config.get('rundir')):
        filename, extension = path.split('.')
        if extension != 'pid':
            continue
        parts = filename.split('-')
        if len(parts) < 2 or parts.pop(0) != 'device':
            continue
        deviceName = '-'.join(parts)
        pid = isRunning(deviceName)
        result[deviceName] = pid
    return result
        

def getPid(deviceId):
    pidFile = getPidFile(deviceId)
    if not os.path.exists(pidFile):
        return None
    with open(pidFile, 'r') as fp:
        pid = fp.read().strip()
    if pid:
        return int(pid)
    return None

def setPid(deviceId, pid):
    pidFile = getPidFile(deviceId)
    with open(pidFile, 'w') as fp:
        fp.write('%s' % pid)

def delPid(deviceId):
    pidFile = getPidFile(deviceId)
    if os.path.exists(pidFile):
        os.unlink(pidFile)

def getPidFile(deviceId):
    return '%s/device-%s.pid' % (config.get('rundir'), deviceId)

