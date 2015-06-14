from chains.common import introspect, utils, log, ChainsException, ParameterException, NoSuchDeviceException, NoSuchActionException
from chains.common.amqp import AmqpDaemon
from chains.device import config
import os, threading, time

def factory(conf):
    if not conf.get('class'):
        raise Exception('Missing main.class in config')
    obj = utils.newObject(
        "chains.devices.%s" % conf.get('class').lower(),
        "%sDevice" % conf.get('class'),
        args=[conf]
    )
    return obj


class DeviceThread(threading.Thread):
    '''
    DeviceThread - Run method in a separate thread.

    This is a pretty plain Thread that is used by
    start() to run onStart() and listenForActions()
    so that they do not block.
    '''
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func
        self.setDaemon(True)
    def run(self):
        self.func()

class Device(AmqpDaemon):
    '''
    Device - base class for all devices

    A Device's mission is to send events and respond to actions.
    Typical approach for a device is this:

    == Init ==
    In onInit(), do any setup-tasks that does not block forever,
    like making sure relevant config settings are okay, opening
    a serial port, checking for needed files etc.

    == Run ==
    In onStart(), do any "while true do this" tasks that block forever,
    like polling values from an external interface and sending events,
    or running a webserver that listens forever, or reading from the
    serial port etc.

    == Actions ==
    Implement a number of cmd_xxx() functions, one for each action
    that the device can perform.

    == Shutdown ==
    In onShutdown() do any cleanup tasks if necceceary.
    Note however that this is not guaranteed to be run!

    == Describe ==
    In onDescribe() describe the various events that the device
    can send. You can also describe the actions, but if you use
    the cmd_xxx() approach, you should not need to.
    Implementing onDescribe() is optional, but should be done
    (eventually) to lay the grounds for a nice rules-creation-gui
    in the future.

    See documentation of each method below for more info.
    '''

    # Signals that shutdown is in progress.
    # If this is changed to True (by shutdown()),
    # then any "while forever do this and that" loops
    # should shop doing whatever they're doing.
    _shutdown = False

    # =============================================
    # Core functions,
    # that should (usually) not be overriden.
    # =============================================

    def __init__(self, config):
        AmqpDaemon.__init__(self, 'device', config.get('id')) #, sendHeartBeat=True)
        self.config = config
        self.eventThread = None
        self.actionThread = None
        self.onInit()

    def start(self, block=False):
        '''
        Run the device

        Will start main loop, onStart(), in a separate thread,
        and then start listening for incoming actions.

        This function should typically NOT be overridden.
        Your device's custom main loop code should be implemented in onStart() instead.
        '''

        # Send an event about being online
        self.sendOnlineEvent()

        # @todo: shutdown of loop
        #   - how to break loop(s) when shutdown() is called
        #   - up to each device to implement?

        # Do main loop, i.e. onStart(), in a separate thread
        # (It will typically do stuff and call onEvent() to
        # push events to the queue).
        log.info('Starting thread for onStart')
        self.eventThread = DeviceThread(self.onStart)
        self.eventThread.start()

        if block:
            self.listen()
        else:
            self.actionThread = DeviceThread(self.listen)
            self.actionThread.start()


    def shutdown(self):
        AmqpDaemon.shutdown(self)
        #log.info('Shutdown called')
        #self._shutdown = True
        # Send an action message to ourself to make sure
        # we break out of the wait-loop for actions asap.
        #log.info('Send _shutdown action')
        #self.sendShutdownAction()
        #log.info('Wait 0.5')
        time.sleep(0.5)
        log.info('Joining actionThread')
        if self.actionThread:
            try:
                self.actionThread.join()
            except RuntimeError, e:
                log.warn('Ignoring exception about joining actionThread: %s' % e)
        log.info('actionThread done')
        log.info('Running onShutdown()')
        try:
            self.onShutdown()
        except Exception, e:
            log.warn('Ignoring exception during onShutdown: %s' % e)
        log.info('Finished running onShutdown()')
        log.info('Joining eventThread')
        if self.eventThread:
            try:
                self.eventThread.join()
            except RuntimeError, e:
                log.warn('Ignoring exception about joining eventThread: %s' % e)
        log.info('eventThread done')
        # Send an event about being online
        log.info('Send offline event')
        try:
            self.sendOfflineEvent()
        except Exception, e:
            log.warn('Ignoring exception during sendOfflineEvent: %s' % e)
        time.sleep(1)
        log.info('Shutdown complete')

    # =============================================
    # Lifecycle functions,
    # that can be implemented as needed.
    # None of these are required.
    # =============================================

    def onInit(self):
        '''
        Initialize device

        Any initialization tasks that DO NOT BLOCK
        forever should be implemented here.

        Only AFTER this function returns, is the device considered
        "online". An event will then be sent to signal this, and
        the lifecycle will proceed to onStart().
        '''
        pass

    def onStart(self):
        '''
        Main loop

        Any continous work that the device does, that
        blocks forever (or for a long time), should be done here
        (like polling sensors, wathing a serial line, running a webserver, etc).

        The device is considered "online" BEFORE this function is called,
        so it should not do setup-tasks that needs to be run f.ex. before
        the device can respond to actions.
        '''
        pass

    def onShutdown(self):
        '''
        Shutdown device

        Do any cleanup tasks here, like closing serial ports etc.

        This function will be called when the manager is asked to
        shut down a device. Note however that it is not guaranteed to
        run (f.ex. if the manager is killed with -9).
        '''
        pass

    #def onDescribe(self):
    #   See AmqpDaemon.onDescribe()

if __name__ == '__main__':
    import sys, time
    if len(sys.argv) < 2:
        print 'usage: device.py deviceId'
        sys.exit(1)
    log.info('Initializing device: %s' % sys.argv[1])
    dev = factory(sys.argv[1])
    log.info('Start device')
    try:
        dev.start(block=True)
        """
        dev.start() #block=True)
        print 'Sleep 5 before shutdown'
        time.sleep(5)
        print 'Now shutdown'
        dev.shutdown()
        """
    except KeyboardInterrupt, e:
        print 'Stopping...'
        dev.shutdown()
        #time.sleep(2)
    print 'Exit'

