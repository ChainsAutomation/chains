# ******************************************
#
# Python wrapper for libtelldus on Linux
#
# Developed by David Karlsson
#             (david.karlsson.80@gmail.com)
#
# Released as is without any garantees on
# functionality.
#
# *******************************************
import platform
import time
from ctypes import c_int, c_ubyte, c_void_p, c_char_p, POINTER, string_at

debug = False

#platform specific imports and CFUNC definitions:
if (platform.system() == 'Windows'):
    #Windows
    from ctypes import windll, WINFUNCTYPE
    tdlib = windll.LoadLibrary('TelldusCore.dll')

    DEVICEFUNC = WINFUNCTYPE(None, c_int, c_int, c_char_p, c_int, c_void_p)
    DEVICECHANGEFUNC = WINFUNCTYPE(None, c_int, c_int, c_int, c_int, c_void_p)
    SENSORFUNC = WINFUNCTYPE(None, c_char_p, c_char_p, c_int, c_int, c_char_p, c_int, c_int, c_void_p)
    RAWDEVICEFUNC = WINFUNCTYPE(None, c_char_p, c_int, c_int, c_void_p)

else:
    if (platform.system() == 'Darwin'):
    #Mac
        from ctypes import cdll, CFUNCTYPE
        tdlib = cdll.LoadLibrary('/Library/Frameworks/TelldusCore.framework/TelldusCore')
    else:
    #Linux
        from ctypes import cdll, CFUNCTYPE
        tdlib = cdll.LoadLibrary('libtelldus-core.so.2')

    DEVICEFUNC = CFUNCTYPE(None, c_int, c_int, c_char_p, c_int, c_void_p)
    DEVICECHANGEFUNC = CFUNCTYPE(None, c_int, c_int, c_int, c_int, c_void_p)
    SENSORFUNC = CFUNCTYPE(None, c_char_p, c_char_p, c_int, c_int, c_char_p, c_int, c_int, c_void_p)
    RAWDEVICEFUNC = CFUNCTYPE(None, c_char_p, c_int, c_int, c_void_p)


#Service methods
TELLSTICK_TURNON =         1
TELLSTICK_TURNOFF =        2
TELLSTICK_BELL =           4
TELLSTICK_TOGGLE =         8
TELLSTICK_DIM =           16
TELLSTICK_LEARN =         32
TELLSTICK_EXECUTE =       64
TELLSTICK_UP =           128
TELLSTICK_DOWN =         256
TELLSTICK_STOP =         512

methodsReadable = {1: 'ON',
                   2: 'OFF',
                   4: 'BELL',
                   8: 'TOGGLE',
                   16: 'DIM',
                   32: 'LEARN',
                   64: 'EXECUTE',
                   128: 'UP',
                   256: 'DOWN',
                   512: 'STOP'}



#Sensor value types
TELLSTICK_TEMPERATURE =    1
TELLSTICK_HUMIDITY =       2

sensorValueTypeReadable = {TELLSTICK_TEMPERATURE: 'Temperature',
                           TELLSTICK_HUMIDITY: 'Humidity'}

#Error codes
TELLSTICK_SUCCESS =                       0
TELLSTICK_ERROR_NOT_FOUND =              -1
TELLSTICK_ERROR_PERMISSION_DENIED =      -2
TELLSTICK_ERROR_DEVICE_NOT_FOUND =       -3
TELLSTICK_ERROR_METHOD_NOT_SUPPORTED =   -4
TELLSTICK_ERROR_COMMUNICATION =          -5
TELLSTICK_ERROR_CONNECTING_SERVICE =     -6
TELLSTICK_ERROR_UNKNOWN_RESPONSE =       -7
TELLSTICK_ERROR_SYNTAX =                 -8
TELLSTICK_ERROR_BROKEN_PIPE =            -9
TELLSTICK_ERROR_COMMUNICATING_SERVICE = -10
TELLSTICK_ERROR_CONFIG_SYNTAX =         -11
TELLSTICK_ERROR_UNKNOWN =               -99

#Controller typedef
TELLSTICK_CONTROLLER_TELLSTICK =          1
TELLSTICK_CONTROLLER_TELLSTICK_DUO =      2
TELLSTICK_CONTROLLER_TELLSTICK_NET =      3

#Service changes
TELLSTICK_DEVICE_ADDED =                  1
TELLSTICK_DEVICE_CHANGED =                2
TELLSTICK_DEVICE_REMOVED =                3
TELLSTICK_DEVICE_STATE_CHANGED =          4

#Change types
TELLSTICK_CHANGE_NAME =                   1
TELLSTICK_CHANGE_PROTOCOL =               2
TELLSTICK_CHANGE_MODEL =                  3
TELLSTICK_CHANGE_METHOD =                 4
TELLSTICK_CHANGE_AVAILABLE =              5
TELLSTICK_CHANGE_FIRMWARE =               6


methodsSupportedDefault = 0

_callbackFuncs = {}




def getNumberOfServices():
    return tdlib.tdGetNumberOfServices()

def getServiceId(i):
    return tdlib.tdGetServiceId(int(i))

def getServiceIdFromStr(s):
    try:
        id = int(s)
        devId = getServiceId(id)
        return devId, getName(devId)
    except:
        pass

    for i in range(getNumberOfServices()):
        if s == getName(getServiceId(i)):
            return getServiceId(i), s

    return -1, 'UNKNOWN'


def getName(id):
    getNameFunc = tdlib.tdGetName
    getNameFunc.restype = c_void_p

    vp = getNameFunc(id)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround, mac crashes on next line
        tdlib.tdReleaseString(vp)

    return s

def methods(id, methodsSupported = None, readable = False):
    if methodsSupported == None:
        methodsSupported = methodsSupportedDefault

    methods = tdlib.tdMethods(id, methodsSupported)
    if readable:
        l = []
        for m in methodsReadable:
            if methods & m:
                l.append(methodsReadable[m])
        return ','.join(l)

    return methods

def turnOn(intServiceId):
    return tdlib.tdTurnOn(intServiceId)

def turnOff(intServiceId):
    return tdlib.tdTurnOff(intServiceId)

def bell(intServiceId):
    return tdlib.tdBell(intServiceId)

def dim(intServiceId, level):
    return tdlib.tdDim(intServiceId, level)

def up(intServiceId):
    return tdlib.tdUp(intServiceId)

def down(intServiceId):
    return tdlib.tdDown(intServiceId)

def stop(intServiceId):
    return tdlib.tdStop(intServiceId)

def learn(intServiceId):
    return tdlib.tdLearn(intServiceId)

def lastSentCommand(intServiceId, methodsSupported = None, readable = False):
    if methodsSupported == None:
        methodsSupported = methodsSupportedDefault

    if readable:
        return methodsReadable.get(tdlib.tdLastSentCommand(intServiceId, methodsSupported), 'UNKNOWN')

    return tdlib.tdLastSentCommand(intServiceId, methodsSupported)

def lastSentValue(intServiceId):
    func = tdlib.tdLastSentValue
    func.restype = c_char_p

    ret = func(intServiceId)
    
#Release string here?
    return ret

def getErrorString(intErrorNo):
    getErrorStringFunc = tdlib.tdGetErrorString
    getErrorStringFunc.restype = c_void_p

    vp = getErrorStringFunc(intErrorNo)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround, mac crashes on nest line
        tdlib.tdReleaseString(vp)

    return s

def addService():
    return tdlib.tdAddService()

def removeService(intServiceId):
    return tdlib.tdRemoveService(intServiceId)

def setName(intServiceId, chNewName):
    if not isinstance(chNewName, str):
        raise ValueError('chNewName needs to be a str')
    if not isinstance(intServiceId, int):
        raise ValueError('intServiceId needs to be an integer')

    return tdlib.tdSetName(intServiceId, chNewName)
    
def getProtocol(intServiceId):
    if not isinstance(intServiceId, int):
        raise ValueError('intServiceId needs to be an integer')
    
    tdGetProtocolFunc = tdlib.tdGetProtocol
    tdGetProtocolFunc.restype = c_void_p

    vp = tdGetProtocolFunc(intServiceId)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround
        tdlib.tdReleaseString(vp)

    return s

def getModel(intServiceId):
    if not isinstance(intServiceId, int):
        raise ValueError('intServiceId needs to be an integer')
    
    tdGetModelFunc = tdlib.tdGetModel
    tdGetModelFunc.restype = c_void_p

    vp = tdGetModelFunc(intServiceId)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround:
        tdlib.tdReleaseString(vp)

    return s

def getServiceParameter(intServiceId, strName, defaultValue):
    if not isinstance(intServiceId, int):
        raise ValueError('intServiceId needs to be an integer')
    if not isinstance(strName, str):
        raise ValueError('strName needs to be a str')
    if not isinstance(defaultValue, str):
        raise ValueError('defaultValue needs to be a str')


    tdGetServiceParameterFunc = tdlib.tdGetServiceParameter
    tdGetServiceParameterFunc.restype = c_void_p

    vp = tdGetServiceParameterFunc(intServiceId, strName, defaultValue)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround:
        tdlib.tdReleaseString(vp)

    return s


def init(defaultMethods = 0):
#defaultMethods could be one or many from: TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN | TELLSTICK_EXECUTE | TELLSTICK_UP | TELLSTICK_DOWN | TELLSTICK_STOP

    global methodsSupportedDefault

    methodsSupportedDefault = defaultMethods


    if (platform.system() == 'Windows'):
    #Windows
        tdlib = windll.LoadLibrary('TelldusCore.dll') #import our library
    elif (platform.system() == 'Darwin'):
        tdlib = cdll.LoadLibrary('/Library/Frameworks/TelldusCore.framework/TelldusCore')
    else:
    #Linux
        tdlib = cdll.LoadLibrary('libtelldus-core.so.2') #import our library

    tdlib.tdInit()




def close():
    tdlib.tdClose()




callbacks = {'lastAdd': 0,
             'serviceEvent': {},
             'serviceChangeEvent': {},
             'sensorEvent': {},
             'rawServiceEvent': {}
             }

def serviceEvent(serviceId, method, data, callbackId, context):
    if debug:
        print 'ServiceEvent'
        print '  serviceId:', serviceId
        print '  method:', method
        print '  data:', data
        print '  callbackId:', callbackId
        print '  context:', context

    for key in callbacks['serviceEvent']:
        f = callbacks['serviceEvent'][key]
        try:
            f(serviceId, method, data, callbackId)
        except:
            print 'Error calling registered callback for serviceEvent'
            if debug:
                raise

def serviceChangeEvent(serviceId, changeEvent, changeType, callbackId, context):
    if debug:
        print 'ServiceChangeEvent'
        print 'serviceId:', serviceId
        print 'changeEvent:', changeEvent
        print 'changeType:', changeType
        print 'callbackId:', callbackId

    for key in callbacks['serviceChangeEvent']:
        f = callbacks['serviceChangeEvent'][key]
        try:
            f(serviceId, changeEvent, changeType, callbackId)
        except:
            print 'Error calling registered callback for serviceChangeEvent'
            if debug:
                raise


def sensorEvent(protocol, model, id, dataType, value, timestamp, callbackId, context):
    if debug:
        print 'SensorEvent'
        print '  protocol:', protocol
        print '  model:', model
        print '  id:', id
        print '  datatype:', dataType
        print '  value:', value
        print '  timestamp:', timestamp
        print '  callbackId:', callbackId
        print '  context:', context

    for key in callbacks['sensorEvent']:
        f = callbacks['sensorEvent'][key]
        try:
            f(protocol, model, id, dataType, value, timestamp, callbackId)
        except:
            print 'Error calling registered callback for sensorEvent'
            if debug:
                raise

def rawServiceEvent(data, controllerId, callbackId, context):
    if debug:
        print 'RawServiceEvent'
        print '  data:', data
        print '  controllerId:', controllerId
        print '  callbackId:', callbackId
        print '  context:', context

    for key in callbacks['rawServiceEvent']:
        f = callbacks['rawServiceEvent'][key]
        try:
            f(data, controllerId, callbackId)
        except:
            print 'Error calling registered callback for rawServiceEvent'
            if debug:
                raise


service_func = DEVICEFUNC(serviceEvent)
_callbackFuncs['service'] = service_func

serviceChange_func = DEVICECHANGEFUNC(serviceChangeEvent)
_callbackFuncs['serviceChange'] = serviceChange_func

sensor_func = SENSORFUNC(sensorEvent)
_callbackFuncs['sensor'] = sensor_func
    
rawService_func = RAWDEVICEFUNC(rawServiceEvent)
_callbackFuncs['raw'] = rawService_func


def registerEvent(func, eventType):

    global callbacks
    if len(callbacks[eventType]) == 0:
        #if first registration of this type of callback
        # register the handler
        if eventType == 'serviceEvent':
            _callbackFuncs['serviceCallbackId'] = tdlib.tdRegisterServiceEvent(_callbackFuncs['service'], 0)
        elif eventType == 'serviceChangeEvent':
            _callbackFuncs['serviceChangeCallbackId'] = tdlib.tdRegisterServiceChangeEvent(_callbackFuncs['serviceChange'], 0)
        elif eventType == 'sensorEvent':
            _callbackFuncs['sensorCallbackId'] = tdlib.tdRegisterSensorEvent(_callbackFuncs['sensor'], 0)
        elif eventType == 'rawServiceEvent':
            _callbackFuncs['rawCallbackId'] = tdlib.tdRegisterRawServiceEvent(_callbackFuncs['raw'], 0)
        else:
            print 'Unknown event type', eventType

        
    callbacks[eventType][callbacks['lastAdd']] = func

    id = callbacks['lastAdd']
    callbacks['lastAdd'] += 1

    return id

def registerServiceEvent(func):
    return registerEvent(func, 'serviceEvent')

def registerServiceChangedEvent(func):
    return registerEvent(func, 'serviceChangeEvent')

def registerSensorEvent(func):
    return registerEvent(func, 'sensorEvent')
    
def registerRawServiceEvent(func):
    return registerEvent(func, 'rawServiceEvent')

def unregisterCallback(callbackId):
    global callbacks
    
    if callbackId in callbacks['serviceEvent']:
        del callbacks['serviceEvent'][callbackId]
        if len(callbacks['serviceEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['serviceCallbackId'])
            del _callbackFuncs['serviceCallbackId']
            
    elif callbackId in callbacks['serviceChangeEvent']:
        del callbacks['serviceChangeEvent'][callbackId]
        if len(callbacks['serviceChangeEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['serviceChangeCallbackId'])
            del _callbackFuncs['serviceChangeCallbackId']

    elif callbackId in callbacks['sensorEvent']:
        del callbacks['sensorEvent'][callbackId]
        if len(callbacks['sensorEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['sensorCallbackId'])
            del _callbackFuncs['sensorCallbackId']

    elif callbackId in callbacks['rawServiceEvent']:
        del callbacks['rawServiceEvent'][callbackId]
        if len(callbacks['rawServiceEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['rawCallbackId'])
            del _callbackFuncs['rawCallbackId']


def setProtocol(intServiceId, strProtocol):
    return tdlib.tdSetProtocol(intServiceId, strProtocol)

def setModel(intServiceId, strModel):
    return tdlib.tdSetModel(intServiceId, strModel)

def setServiceParameter(intServiceId, strName, strValue):
    return tdlib.tdSetServiceParameter(intServiceId, strName, strValue)

#Completly untested calls
def connectTellStickController(vid, pid, serial):
    tdlib.tdConnectTellStickController(vid, pid, serial)

def disconnectTellStickController(vid, pid, serial):
    tdlib.tdDisConnectTellStickController(vid, pid, serial)


#Missing support for these API calls:
#
#int tdRegisterControllerEvent( TDControllerEvent eventFunction, void *context);
#int tdSendRawCommand(const char *command, int reserved);    

if __name__ == '__main__':
    def cb(data,controllerId,callbackId):
        print 'RawServiceEvent'
        print '  data:', data
        print '  controllerId:', controllerId
        print '  callbackId:', callbackId
        print '  context:', context

    registerRawServiceEvent(cb)
    import time
    while True:
        time.sleep(0.5)

if __name__ == 'x__main__':
    import time

    init(defaultMethods = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN)

    print 'getNumberOfServices', getNumberOfServices()
    
    print 'Id\tName'
    for i in range(getNumberOfServices()):
        devId = getServiceId(i)
        print devId, getName(devId), methods(devId)


    if 1: #0:
        print 'Methods(1)', methods(1)
        print 'methods(1, readable=True)', methods(1, readable = True)
        print 'methods(3124, readable=True)', methods(3124, readable = True)
        print 'TurnOn(1)', turnOn(1)
        time.sleep(1)
        print 'TurnOff(1)', turnOff(1)
        time.sleep(1)
        print 'Dim (1, 121)', dim(1, 121)
    
        print 'LastSentCommand(1)', lastSentCommand(1)
        print 'LastSentValue(1)', lastSentValue(1)
        print 'GetErrorString(-2)', getErrorString(-2)
        
    print 'getServiceIdFromStr', getServiceIdFromStr('2')    
    print 'getServiceIdFromStr', getServiceIdFromStr('Vardagsrum')
    print 'getServiceIdFromStr', getServiceIdFromStr('234')


    devId = addService()
    if devId > 0:
        print 'AddService', devId
        print 'setName', repr(setName(devId, 'Test'))
        print 'getName', repr(getName(devId))
        print 'getProtocol', getProtocol(devId)
        print 'setProtocol', setProtocol(devId, 'arctech')
        print 'getProtocol', getProtocol(devId)

        print 'getModel', getModel(devId)
        print 'setModel', setModel(devId, 'selflearning-switch')
        print 'getModel', getModel(devId)

        print 'getServiceParameter (unit)', repr(getServiceParameter(devId, "unit", ""))
        print 'setServiceParameter (unit)', repr(setServiceParameter(devId, 'unit', '123'))                                       
        print 'getServiceParameter (unit)', repr(getServiceParameter(devId, "unit", ""))

        print 'getServiceParameter (house)', repr(getServiceParameter(devId, "house", ""))
        print 'setServiceParameter (house)', repr(setServiceParameter(devId, "house", "321"))
        print 'getServiceParameter (house)', repr(getServiceParameter(devId, "house", ""))

        print '\n\nId\tName'
        for i in range(getNumberOfServices()):
            devId = getServiceId(i)
            print devId, getName(devId), methods(devId)
    
        print 'Remove Service', removeService(devId)

    else:
        print 'addService returned error', getErrorString(devId)

    print '\n\nId\tName'
    for i in range(getNumberOfServices()):
        devId = getServiceId(i)
        print devId, getName(devId), methods(devId)


    print 'Done with unit test'
