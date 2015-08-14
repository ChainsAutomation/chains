import amqplib.client_0_8 as amqp
import chains.common.jsonlib as json
from chains.common import log, utils, config, ChainsException, NoSuchActionException, introspect
import time, threading, socket, sys, signal
import amqplib.client_0_8.exceptions

PREFIX_DEVICE             = 'd'
PREFIX_MANAGER            = 'm'
PREFIX_REACTOR            = 'r'
PREFIX_ORCHESTRATOR       = 'o'

PREFIX_EVENT              = 'e'
PREFIX_ACTION             = 'a'
PREFIX_ACTION_RESPONSE    = 'r'
PREFIX_ACTION_ERROR       = 'x'
PREFIX_HEARTBEAT_REQUEST  = 'H'
PREFIX_HEARTBEAT_RESPONSE = 'h'

HEARTBEAT_VALUE_OFFLINE  = 0
HEARTBEAT_VALUE_ONLINE   = 1
HEARTBEAT_VALUE_RESPONSE = 2
HEARTBEAT_VALUE_REQUEST  = 3

class TimeoutException(Exception):
    pass

class RemoteException(ChainsException):
    pass

def getUuid():
    import uuid # this takes a little while, so don't do it before we need it
    return str(uuid.uuid4())

class ConnectionNotReadyException(Exception):
    pass

class Connection:

    def __init__(self):

        conf = config.ConnectionConfig()
        conf.reload()

        #log.info("Host: %s Port: %s" % (conf.get('host'),conf.get('port')))

        if not conf.get('host'):
            raise ConnectionNotReadyException('Connection config not present yet')

        host     = conf.get('host')
        port     = conf.get('port')
        exchange = conf.get('exchange')
        user     = conf.get('user')
        password = conf.get('password')
        ssl      = conf.getBool('ssl')

        if not port:     port     = '5672'
        if not exchange: exchange = 'chains'
        if not user:     user     = 'guest'
        if not password: password = 'guest'

        self.channels  = []
        self.address   = '%s:%s' % (host, port)
        self.exchange  = exchange
        self.user      = user
        self.password  = password
        self.ssl       = ssl

        self.conn      = amqp.Connection(
            self.address,
            userid = self.user,
            password = self.password,
            ssl = self.ssl
        )

    def producer(self, **kw):
        o = Producer(self, **kw)
        self.channels.append(o)
        return o

    def consumer(self, keys=None, **kw):
        if not keys:
            keys = []
        o = Consumer(self, keys=keys, **kw)
        self.channels.append(o)
        return o

    #def rpc(self, keys=None, queuePrefix=None):
    def rpc(self, queuePrefix=None):
        o = Rpc(self, queuePrefix=queuePrefix)
        self.channels.append(o)
        return o

    def close(self):
        items = []
        if self.channels:
            for item in self.channels:
                items.append(('channel', item))
        if self.conn:
            items.append(('connection', self.conn))
        if self.conn.transport and self.conn.transport.sock:
            items.append(('socket', self.conn.transport.sock))
        for type, obj in items:
            #log.info('Try close %s: %s' % (type,obj))
            try: obj.close()
            except Exception, e: log.warn('Ignoring fail on close %s: %s' % (type,e))
        self.channels = []
        self.conn = None

class Channel:

    def __init__(self, conn, **kw):
        self.consumeKeys = None
        self.conn = conn
        self.ch = self.conn.conn.channel()
        self.exchange = self.conn.exchange
        if kw.has_key('queueName'):
            self.queueName = kw['queueName']
        elif kw.has_key('queuePrefix'):
            self.queueName = '%s-%s' % (kw['queuePrefix'],getUuid())
        else:
            self.queueName = 'unnamed-%s' % (getUuid())
        if kw.has_key('noAck') and kw['noAck']:
            self.noAck = True
        else:
            self.noAck = False

    def close(self, closeConnection=False):
        if self.ch:
            if self.consumeKeys:
                for key in self.consumeKeys:
                    try:
                        self.ch.queue_unbind(self.queueName, self.exchange, key)
                    except Exception, e:
                        # don't pollute log if is not found
                        isNotFound = False
                        try:
                            if e.args[0] == 404:
                                isNotFound = True
                        except:
                            pass
                        if not isNotFound:
                            log.info('Ignore fail to unbind queue %s from %s for %s: %s' % (self.queueName, self.exchange, key, e))
            try:
                self.ch.queue_delete(queue=self.queueName)
            except Exception, e:
                log.debug('Ignore fail to delete queue: %s' % e)
            try:
                self.ch.close()
            except Exception, e:
                log.info('Ignore fail to close channel object: %s' % e)
            self.ch = None

        if self.conn:
            if closeConnection:
                try:
                    self.conn.close()
                except Exception, e:
                    log.info('Ignore fail to close connection: %s' % e)

    def exchange_declare(self):
        self.ch.exchange_declare(self.exchange, 'topic', auto_delete=True)

    def queue_declare(self, exclusive=False):
        queueName = 'chains.%s' % (self.queueName)
        self.queue, nMsg, nConsumers = self.ch.queue_declare(
            durable=False,
            queue=queueName,
            auto_delete=True,
            exclusive=exclusive
            # skip this, because in some circumstances connections seems
            # to hang in there even after disconnect.
            # f.ex. if i start chains manager on my raspbmc and reboot it,
            # rabbit still shows it as connected, and when it boots back up
            # it cannot connect because the old connection holds queue exclusively
            #exclusive=True
        )

class Producer(Channel):
    def __init__(self, *args, **kw):
        Channel.__init__(self, *args, **kw)
        self.ch.access_request('/data', active=True, read=False, write=True)
        self.exchange_declare()
        if kw.has_key('autoCorrelationId'):
            self.autoCorrelationId = kw['autoCorrelationId']
        else:
            self.autoCorrelationId = False

    def put(self, key, message, correlationId=None):
        if not correlationId and self.autoCorrelationId:
            correlationId = getUuid() #str(uuid.uuid4())
        if correlationId:
            msg = amqp.Message(
                json.encode(message),
                content_type='text/json',
                correlation_id = correlationId
            )
        else:
            msg = amqp.Message(
                json.encode(message),
                content_type='text/json'
            )
        self.ch.basic_publish(msg, self.exchange, key)
        return correlationId
            

class Consumer(Channel):

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

        keys = None
        if kwargs.has_key('keys'):
            keys = kwargs['keys']
            del kwargs['keys']
        if not keys:
            keys = ['#']
        self.consumeKeys = keys

        self.ch.access_request('/data', active=True, read=True, write=False)
        self.exchange_declare()
        self.queue_declare()

        log.info("Consume keys: %s" % keys)
        for key in keys:
            log.info('Bind queue to key: %s' % key)
            self.ch.queue_bind(self.queue, self.exchange, key)

        self.messages = []
        self.deliveryTag = None
        self.consumerTag = self.ch.basic_consume(self.queue, callback=self._callback)

    def get(self):
        if self.deliveryTag is not None:
            raise Exception('You must call ack() before getting a new item')
        while not self.messages:
            self.ch.wait()
        msg = self.messages.pop(0)
        try:
            data = json.decode(msg.body)
        except Exception, e:
            raise Exception("Failed decoding JSON: %s\nOrig exception: %s" % (msg.body, e))
        self.deliveryTag = msg.delivery_tag
        correlationId = None
        if msg.properties.has_key('correlation_id'):
            correlationId = msg.properties['correlation_id']
        return (msg.routing_key, data, correlationId)

    def _callback(self, msg):
        self.messages.append(msg)

    def ack(self):
        assert self.deliveryTag is not None
        if not self.noAck:
            self.ch.basic_ack(self.deliveryTag)
        self.deliveryTag = None

class Rpc(Channel):

    def __init__(self, conn, queuePrefix=None):
        if not queuePrefix:
            queuePrefix = 'unspecified-rpc'
        Channel.__init__(self, conn, queuePrefix=queuePrefix)
        keys = ['#']
        self.consumeKeys = keys
        self.ch.access_request('/data', active=True, read=True, write=True) #False)
        self.exchange_declare()
        # these should be exclsive or they don't auto-delete for some reason
        self.queue_declare(exclusive=True)
        for key in keys:
            log.notice('Listen to: %s' % key)
            self.ch.queue_bind(self.queue, self.exchange, key)
        self.deliveryTag = None
        self.correlationId = None
        self.response = None

    def _callback(self, msg):
        log.notice('RPC-CALL: callback seen: %s = %s' % (msg.routing_key, msg.body))
        res = None
        if len(msg.routing_key) > 1 and msg.routing_key[1] in ['r','x'] and msg.properties.has_key('correlation_id') and msg.properties['correlation_id'] == self.correlationId:
	    log.notice('RPC-CALL: callback matched: %s = %s' % (msg.routing_key, msg.body))
            self.response = msg
            res = True
        else:
            res = False
        if not self.noAck and res:
            self.ch.basic_ack(msg.delivery_tag)
        return res

    def call(self, key, data=None, timeout=5, block=None):
        log.debug('RPC-CALL: execute %s = %s' % (key, data))
        if block == None:
            block = True

        # @todo: remove consume again afterwards!
        if not timeout:
            # tuba - no_ack=True is also an option
            self.consumerTag = self.ch.basic_consume(self.queue, callback=self._callback)

        self.response = None
        self.correlationId = getUuid() #str(uuid.uuid4())
        msg = amqp.Message(
            json.encode(data),
            content_type='text/json',
            correlation_id = self.correlationId,
            #reply_to = self.queue
        )
        self.ch.basic_publish(
            msg,
            self.exchange,
            key,
            #reply_to = self.queue,
            #correlation_id = self.correlationId
        )

        if not block:
            return
        log.notice('RPC-CALL: wait response')

        startTime = time.time()
        while self.response is None:
            if timeout:
                msg = self.ch.basic_get(self.queue)
                if msg:
                    if self._callback(msg):
                        break
                else:
                    time.sleep(0.01)
                    if (time.time()-startTime) >= timeout:
                        raise TimeoutException('Waited %s sec for rpc call %s' % (timeout, key))
            else:
                self.ch.wait()

        log.notice('RPC-CALL: finished waiting')
        try:
            body = json.decode(self.response.body)
        except Exception, e:
            raise Exception("json decoding error: %s - for raw response: %s" % (e, self.response.body))
        tmp = self.response.routing_key.split('.')
        if tmp[0][1] == 'x': # todo: use constants
            raise RemoteException(body)
        log.debug('RPC-CALL: respone %s = %s' % (self.response.routing_key, body))
        return body

class AmqpDaemon:

    def __init__(self, type, id):
        self.type      = type
        self.id        = id
        if type and id:
            self.queueName = '%s-%s' % (type,id)
        elif not type:
            self.queueName = 'unspecified-daemon-type-%s' % id
        elif not id:
            raise Exception('Must have daemon id')
        self.connect()

    def _connect(self):
        self.connection = Connection()
        self.producer = self.connection.producer(queueName=self.queueName)
        self.consumer = self.connection.consumer(self.getConsumeKeys(), queueName=self.queueName)
        self._shutdown = False

    def connect(self):

        self.connection = None

        try:
            self._connect()
        except ConnectionNotReadyException, e:
            self.reconnect(e)

    def reconnect(self, e):
        if self.connection:
            self.connection.close()
        self.producer = None
        self.consumer = None
        self.connection = None
        delay = 2
        retry = 0
        while True:
            retry += 1
            log.error('Attempting to reconnect #%s and continue in %s sec after socket error: %s' % (retry,delay,e))
            time.sleep(delay)
            try:
                self._connect()
                log.error('Successfully reconnected (after %s retries) - back to work!' % (retry))
                return
            except socket.error, e2:
                pass
            except amqplib.client_0_8.exceptions.AMQPConnectionException, e2:
                pass
            except ConnectionNotReadyException, e2:
                pass

    def listen(self):
        log.info('Start listening for messages, topics = %s' % self.getConsumeKeys())
        actionPrefix = self.getActionPrefix()
        heartBeatRequestPrefix = self.getHeartBeatRequestPrefix()
        while not self._shutdown:
            log.notice('Waiting for messages')
            try:
                topic, data, correlationId = self.consumer.get()
            except socket.error, e:
                self.reconnect(e)
                continue
            except amqplib.client_0_8.exceptions.AMQPConnectionException, e:
                self.reconnect(e)
                continue
            except IOError, e:
                self.reconnect(e)
                continue
            except Exception, e:
                log.error('Caught during consumer.get() in listen: %s' % utils.e2str(e))
                raise e
            try:
                self.consumer.ack()
            except Exception, e:
                log.error('Caught during consumer.ack() in listen: %s' % utils.e2str(e))
                raise e
            if self._shutdown:
                log.info('Not handeling topic: %s because self._shutdown = True' % (topic,))
            else:
                log.notice('Handeling topic: %s' % topic)
                tmp = topic.split('.')
                handle = False
                if tmp[0] == actionPrefix and len(tmp) > 1:
                    pre, src, key = tmp
                    if key == '_shutdown':
                        continue
                    if not data:
                        data = []
                    try:
                        result = self.runAction(key, data)
                    except Exception, e:
                        self.sendActionError(key, e, correlationId)
                    else:
                        if result != None or correlationId:
                            self.sendActionResponse(key, result, correlationId)
                elif tmp[0] == heartBeatRequestPrefix:
                    self.sendHeartBeatResponse()
                else:
                    self.onMessage(topic, data, correlationId)
                log.notice('Handeled topic: %s' % topic)
        log.info('Exited listen() loop - self._shutdown = %s' % self._shutdown)

    def runAction(self, key, data):
        try:
            fun = getattr(self, 'action_%s' % (key)) #key[0].upper(), key[1:]))
        except AttributeError:
            raise NoSuchActionException(key)
        else:
            if type(data) == type([]):
                data = tuple(data)
            res = fun(*data)
            return res

    def onMessage(self, topic, data, correlationId):
        pass

    def shutdown(self):
        if self._shutdown:
            log.info('Not shutting down (again) since shutdown already in progress')
            return
        log.info('Shutting down')
        self._shutdown = True
        try:
            self.sendShutdownAction()
            log.debug('Added _shutdown action to queue. Waiting for shutdown')
        # todo: investigate this. possibly switch amqp lib?
        except AttributeError:
            # AttributeError: 'NoneType' object has no attribute 'method_writer'
            # This happens sometimes and is probably because of a bug in amqplib?
            # Hopefully it means that channel is already shut down?
            log.info('Ignoring AttributeError about no method_writer, caused by bug in amqplib(?)')

    def sendHeartBeatEvent(self, data):
        topic = '%s.%s' % (self.getHeartBeatResponsePrefix(), self.id)
        log.notice('sendHeartBeat: %s = %s' % (topic, data))
        self.producer.put(topic, data)

    def sendHeartBeatResponse(self):
        self.sendHeartBeatEvent(HEARTBEAT_VALUE_RESPONSE)

    def sendOnlineEvent(self):
        self.sendHeartBeatEvent(HEARTBEAT_VALUE_ONLINE)

    def sendOfflineEvent(self):
        self.sendHeartBeatEvent(HEARTBEAT_VALUE_OFFLINE)

    def sendEvent(self, key, data):
        topic = '%s.%s.%s' % (self.getEventPrefix(), self.id, key)
        event = {'data': data}
        # device/host + key is "smoer paa flesk" because they are
        # part of topic and can be extracted from it, but keep it
        # untill there is a good reason not to (f.ex. in case
        # we should change topic logic later)
        if self.type == 'device':
            event['device'] = self.id
        else:
            event['host'] = self.id
        event['key'] = key
        log.info('sendEvent: %s = %s' % (topic, event))
        self.producer.put(topic, event)

    def sendManagerAction(self, manager, action, data=None):
        topic = '%s%s.%s.%s' % (PREFIX_MANAGER, PREFIX_ACTION, manager, action)
        self.producer.put(topic, data)

    def sendActionResponse(self, key, data, correlationId):
        topic = '%s.%s.%s' % (self.getActionResponsePrefix(), self.id, key)
        log.debug('sendActionResponse: %s = %s' % (topic, data))
        self.producer.put(topic, data, correlationId)

    def sendActionError(self, key, data, correlationId=None):
        if isinstance(data, Exception):
            data = {'error': True, 'errorMessage': utils.e2str(data)}
        topic = '%s.%s.%s' % (self.getActionErrorPrefix(), self.id, key)
        log.debug('sendActionError: %s = %s' % (topic, data))
        self.producer.put(topic, data, correlationId)

    def sendShutdownAction(self):
        log.info('Put shutdown message to producer - start')
        topic = '%s.%s.%s' % (self.getActionPrefix(), self.id, '_shutdown')
        self.producer.put(topic, 1)
        log.info('Put shutdown message to producer - end')

    def callDaemonAction(self, daemonType, daemonId, action, args=None):
        key = '%s%s.%s.%s' % (self.getDaemonTypePrefix(daemonType), PREFIX_ACTION, daemonId, action)
        rpc = self.connection.rpc(queuePrefix='rpc-webapi')
        return rpc.call(key, data=args)

    def callOrchestratorAction(self, action, args=None):
        return self.callDaemonAction('orchestrator', 'main', action, args=args)

    def callManagerAction(self, managerId, action, args=None):
        return self.callDaemonAction('manager', managerId, action, args=args)

    def callDeviceAction(self, deviceId, action, args=None):
        return self.callDaemonAction('device', deviceId, action, args=args)

    def callReactorAction(self, reactorId, action, args=None):
        return self.callDaemonAction('reactor', reactorId, action, args=args)

    def getHeartBeatRequestPrefix(self): #, type=None):
        #return self.getDaemonTypePrefix(type) + PREFIX_HEARTBEAT_REQUEST
        return PREFIX_HEARTBEAT_REQUEST
    def getHeartBeatResponsePrefix(self):
        return self.getDaemonTypePrefix() + PREFIX_HEARTBEAT_RESPONSE
    def getEventPrefix(self):
        return self.getDaemonTypePrefix() + PREFIX_EVENT
    def getActionPrefix(self):
        return self.getDaemonTypePrefix() + PREFIX_ACTION
    def getActionResponsePrefix(self):
        return self.getDaemonTypePrefix() + PREFIX_ACTION_RESPONSE
    def getActionErrorPrefix(self):
        return self.getDaemonTypePrefix() + PREFIX_ACTION_ERROR

    def getDaemonTypePrefix(self, type=None):
        if not type:
            type = self.type
        if type == 'device':
            return PREFIX_DEVICE
        if type == 'manager':
            return PREFIX_MANAGER
        if type == 'reactor':
            return PREFIX_REACTOR
        if type == 'orchestrator':
            return PREFIX_ORCHESTRATOR

    def getConsumeKeys(self):
        return [
            '%s.%s.*' % (self.getActionPrefix(), self.id),
            self.getHeartBeatRequestPrefix()
        ]

    # Mostly (only?) used for devices, but needs to be in all AmqpDaemons since describe() is
    def onDescribe(self):
        '''
        Describe device capabilities.

        To let the system know what events the device can send,
        and what actions it supports, you should implement
        this method.

        This will f.ex. give you an option to run the device's
        actions via the webgui and in the future, it will be
        the foundation for a nice gui for creating rules using
        drag'n'drop.

        The return value should be a dict like this:

        {
            'info': 'My fantastic device',
            'events': ...event description...
            'actions': ...actions description...
        }

        Note that if you use cmd_xxx() style of actions, you
        do not need to provide a the 'actions' part, it will
        be auto-generated.

        TODO: document the events description
        TODO: document the actions description
        TODO: document how actions description is auto-generated
        ====> these 3 are now in doc/README, to be moved to wiki
        '''
        return {}

    def action_ping(self):
        return "pong"

    def action_shutdown(self):
        '''Shut down daemon'''
        self.shutdown()

    def action_setLogLevel(self, level):
        log.setLevel(level)
        log.warn('Changed loglevel to "%s" during runtime' % level)

    def action_getLogLevel(self):
        return log.getLevel()

    '''
    Describe this device

    This is called by the master->manager to fetch
    the description dict for this device. It will
    again call the onDescribe() function that you
    should implement in your device, and will try
    to fill out and auto-generate any missing parts.

    You should NOT override this method in your device,
    you should rather implement onDescribe().
    '''
    def action_describe(self):
        '''Describe this daemon'''

        # First call the subclass' onDescribe
        ret = {}
        desc = self.onDescribe()

        # INFO

        # If we've got info from subclass onDescribe, use it
        if desc.has_key('info'):
            ret['info'] = desc['info']
        # Or try info from config (best practice) - do this in Device instead?
        #elif self.config.has('info'):
        #    ret['info'] = self.config.get('info')
        # Or indicate not info
        else:
            ret['info'] = ''

        # ACTIONS

        # If we've got actions description from subclass, use it
        if desc.has_key('actions'):
            ret['actions'] = desc['actions']
        # Or automatically describe all cmd_* functions using introspection
        else:
            ret['actions'] = introspect.describeMethods(self, 'action_')

        # EVENTS

        # If we've got events description from subclass, use it
        if desc.has_key('events'):
            ret['events'] = desc['events']
        # If not then noop
        else:
            ret['events'] = []

        return ret


def runWithSignalHandler(daemon):
    def signalHandler(signal, frame):
        daemon.shutdown()
        daemon.sendOfflineEvent()
        sys.exit(0)
    signal.signal(signal.SIGTERM, signalHandler)  # $ kill <pid>
    signal.signal(signal.SIGINT, signalHandler)  # Ctrl-C
    try:
        daemon.run()
    except Exception, e:
        log.error('Daemon crashed: %s' % utils.e2str(e))
        raise e
