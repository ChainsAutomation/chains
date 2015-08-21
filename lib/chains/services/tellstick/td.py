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


#Device methods
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
TELLSTICK_ERROR_CONNECTING_device =     -6
TELLSTICK_ERROR_UNKNOWN_RESPONSE =       -7
TELLSTICK_ERROR_SYNTAX =                 -8
TELLSTICK_ERROR_BROKEN_PIPE =            -9
TELLSTICK_ERROR_COMMUNICATING_device = -10
TELLSTICK_ERROR_CONFIG_SYNTAX =         -11
TELLSTICK_ERROR_UNKNOWN =               -99

#Controller typedef
TELLSTICK_CONTROLLER_TELLSTICK =          1
TELLSTICK_CONTROLLER_TELLSTICK_DUO =      2
TELLSTICK_CONTROLLER_TELLSTICK_NET =      3

#device changes
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




def getNumberOfDevices():
    return tdlib.tdGetNumberOfdevices()

def getdeviceId(i):
    return tdlib.tdGetdeviceId(int(i))

def getdeviceIdFromStr(s):
    try:
        id = int(s)
        devId = getdeviceId(id)
        return devId, getName(devId)
    except:
        pass

    for i in range(getNumberOfdevices()):
        if s == getName(getdeviceId(i)):
            return getdeviceId(i), s

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

def turnOn(intdeviceId):
    return tdlib.tdTurnOn(intdeviceId)

def turnOff(intdeviceId):
    return tdlib.tdTurnOff(intdeviceId)

def bell(intdeviceId):
    return tdlib.tdBell(intdeviceId)

def dim(intdeviceId, level):
    return tdlib.tdDim(intdeviceId, level)

def up(intdeviceId):
    return tdlib.tdUp(intdeviceId)

def down(intdeviceId):
    return tdlib.tdDown(intdeviceId)

def stop(intdeviceId):
    return tdlib.tdStop(intdeviceId)

def learn(intdeviceId):
    return tdlib.tdLearn(intdeviceId)

def lastSentCommand(intdeviceId, methodsSupported = None, readable = False):
    if methodsSupported == None:
        methodsSupported = methodsSupportedDefault

    if readable:
        return methodsReadable.get(tdlib.tdLastSentCommand(intdeviceId, methodsSupported), 'UNKNOWN')

    return tdlib.tdLastSentCommand(intdeviceId, methodsSupported)

def lastSentValue(intdeviceId):
    func = tdlib.tdLastSentValue
    func.restype = c_char_p

    ret = func(intdeviceId)
    
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

def adddevice():
    return tdlib.tdAdddevice()

def removedevice(intDeviceId):
    return tdlib.tdRemovedevice(intDeviceId)

def setName(intdeviceId, chNewName):
    if not isinstance(chNewName, str):
        raise ValueError('chNewName needs to be a str')
    if not isinstance(intdeviceId, int):
        raise ValueError('intdeviceId needs to be an integer')

    return tdlib.tdSetName(intdeviceId, chNewName)
    
def getProtocol(intdeviceId):
    if not isinstance(intdeviceId, int):
        raise ValueError('intdeviceId needs to be an integer')
    
    tdGetProtocolFunc = tdlib.tdGetProtocol
    tdGetProtocolFunc.restype = c_void_p

    vp = tdGetProtocolFunc(intdeviceId)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround
        tdlib.tdReleaseString(vp)

    return s

def getModel(intdeviceId):
    if not isinstance(intdeviceId, int):
        raise ValueError('intdeviceId needs to be an integer')
    
    tdGetModelFunc = tdlib.tdGetModel
    tdGetModelFunc.restype = c_void_p

    vp = tdGetModelFunc(intdeviceId)
    cp = c_char_p(vp)
    s = cp.value
    
    if (platform.system() != 'Darwin'): #Workaround:
        tdlib.tdReleaseString(vp)

    return s

def getdeviceParameter(intDeviceId, strName, defaultValue):
    if not isinstance(intdeviceId, int):
        raise ValueError('intdeviceId needs to be an integer')
    if not isinstance(strName, str):
        raise ValueError('strName needs to be a str')
    if not isinstance(defaultValue, str):
        raise ValueError('defaultValue needs to be a str')


    tdGetdeviceParameterFunc = tdlib.tdGetDeviceParameter
    tdGetdeviceParameterFunc.restype = c_void_p

    vp = tdGetdeviceParameterFunc(intDeviceId, strName, defaultValue)
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
             'deviceEvent': {},
             'deviceChangeEvent': {},
             'sensorEvent': {},
             'rawdeviceEvent': {}
             }

def deviceEvent(serviceId, method, data, callbackId, context):
    if debug:
        print 'deviceEvent'
        print '  deviceId:', serviceId
        print '  method:', method
        print '  data:', data
        print '  callbackId:', callbackId
        print '  context:', context

    for key in callbacks['deviceEvent']:
        f = callbacks['deviceEvent'][key]
        try:
            f(deviceId, method, data, callbackId)
        except:
            print 'Error calling registered callback for deviceEvent'
            if debug:
                raise

def deviceChangeEvent(serviceId, changeEvent, changeType, callbackId, context):
    if debug:
        print 'deviceChangeEvent'
        print 'deviceId:', serviceId
        print 'changeEvent:', changeEvent
        print 'changeType:', changeType
        print 'callbackId:', callbackId

    for key in callbacks['deviceChangeEvent']:
        f = callbacks['deviceChangeEvent'][key]
        try:
            f(deviceId, changeEvent, changeType, callbackId)
        except:
            print 'Error calling registered callback for deviceChangeEvent'
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

def rawdeviceEvent(data, controllerId, callbackId, context):
    if debug:
        print 'RawdeviceEvent'
        print '  data:', data
        print '  controllerId:', controllerId
        print '  callbackId:', callbackId
        print '  context:', context

    for key in callbacks['rawdeviceEvent']:
        f = callbacks['rawdeviceEvent'][key]
        try:
            f(data, controllerId, callbackId)
        except:
            print 'Error calling registered callback for rawdeviceEvent'
            if debug:
                raise


device_func = DEVICEFUNC(serviceEvent)
_callbackFuncs['device'] = service_func

deviceChange_func = DEVICECHANGEFUNC(serviceChangeEvent)
_callbackFuncs['deviceChange'] = serviceChange_func

sensor_func = SENSORFUNC(sensorEvent)
_callbackFuncs['sensor'] = sensor_func
    
rawdevice_func = RAWDEVICEFUNC(rawDeviceEvent)
_callbackFuncs['raw'] = rawdevice_func


def registerEvent(func, eventType):

    global callbacks
    if len(callbacks[eventType]) == 0:
        #if first registration of this type of callback
        # register the handler
        if eventType == 'deviceEvent':
            _callbackFuncs['deviceCallbackId'] = tdlib.tdRegisterDeviceEvent(_callbackFuncs['service'], 0)
        elif eventType == 'deviceChangeEvent':
            _callbackFuncs['deviceChangeCallbackId'] = tdlib.tdRegisterDeviceChangeEvent(_callbackFuncs['serviceChange'], 0)
        elif eventType == 'sensorEvent':
            _callbackFuncs['sensorCallbackId'] = tdlib.tdRegisterSensorEvent(_callbackFuncs['sensor'], 0)
        elif eventType == 'rawdeviceEvent':
            _callbackFuncs['rawCallbackId'] = tdlib.tdRegisterRawdeviceEvent(_callbackFuncs['raw'], 0)
        else:
            print 'Unknown event type', eventType

        
    callbacks[eventType][callbacks['lastAdd']] = func

    id = callbacks['lastAdd']
    callbacks['lastAdd'] += 1

    return id

def registerdeviceEvent(func):
    return registerEvent(func, 'deviceEvent')

def registerdeviceChangedEvent(func):
    return registerEvent(func, 'deviceChangeEvent')

def registerSensorEvent(func):
    return registerEvent(func, 'sensorEvent')
    
def registerRawdeviceEvent(func):
    return registerEvent(func, 'rawdeviceEvent')

def unregisterCallback(callbackId):
    global callbacks
    
    if callbackId in callbacks['deviceEvent']:
        del callbacks['deviceEvent'][callbackId]
        if len(callbacks['deviceEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['deviceCallbackId'])
            del _callbackFuncs['deviceCallbackId']
            
    elif callbackId in callbacks['deviceChangeEvent']:
        del callbacks['deviceChangeEvent'][callbackId]
        if len(callbacks['deviceChangeEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['deviceChangeCallbackId'])
            del _callbackFuncs['deviceChangeCallbackId']

    elif callbackId in callbacks['sensorEvent']:
        del callbacks['sensorEvent'][callbackId]
        if len(callbacks['sensorEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['sensorCallbackId'])
            del _callbackFuncs['sensorCallbackId']

    elif callbackId in callbacks['rawdeviceEvent']:
        del callbacks['rawdeviceEvent'][callbackId]
        if len(callbacks['rawdeviceEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['rawCallbackId'])
            del _callbackFuncs['rawCallbackId']


def setProtocol(intdeviceId, strProtocol):
    return tdlib.tdSetProtocol(intdeviceId, strProtocol)

def setModel(intdeviceId, strModel):
    return tdlib.tdSetModel(intdeviceId, strModel)

def setdeviceParameter(intDeviceId, strName, strValue):
    return tdlib.tdSetdeviceParameter(intDeviceId, strName, strValue)

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
        print 'RawdeviceEvent'
        print '  data:', data
        print '  controllerId:', controllerId
        print '  callbackId:', callbackId
        print '  context:', context

    registerRawdeviceEvent(cb)
    import time
    while True:
        time.sleep(0.5)

if __name__ == 'x__main__':
    import time

    init(defaultMethods = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN)

    print 'getNumberOfdevices', getNumberOfDevices()
    
    print 'Id\tName'
    for i in range(getNumberOfdevices()):
        devId = getdeviceId(i)
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
        
    print 'getdeviceIdFromStr', getDeviceIdFromStr('2')    
    print 'getdeviceIdFromStr', getDeviceIdFromStr('Vardagsrum')
    print 'getdeviceIdFromStr', getDeviceIdFromStr('234')


    devId = adddevice()
    if devId > 0:
        print 'Adddevice', devId
        print 'setName', repr(setName(devId, 'Test'))
        print 'getName', repr(getName(devId))
        print 'getProtocol', getProtocol(devId)
        print 'setProtocol', setProtocol(devId, 'arctech')
        print 'getProtocol', getProtocol(devId)

        print 'getModel', getModel(devId)
        print 'setModel', setModel(devId, 'selflearning-switch')
        print 'getModel', getModel(devId)

        print 'getdeviceParameter (unit)', repr(getDeviceParameter(devId, "unit", ""))
        print 'setdeviceParameter (unit)', repr(setDeviceParameter(devId, 'unit', '123'))                                       
        print 'getdeviceParameter (unit)', repr(getDeviceParameter(devId, "unit", ""))

        print 'getdeviceParameter (house)', repr(getDeviceParameter(devId, "house", ""))
        print 'setdeviceParameter (house)', repr(setDeviceParameter(devId, "house", "321"))
        print 'getdeviceParameter (house)', repr(getDeviceParameter(devId, "house", ""))

        print '\n\nId\tName'
        for i in range(getNumberOfdevices()):
            devId = getdeviceId(i)
            print devId, getName(devId), methods(devId)

        print 'Remove device', removeDevice(devId)

    else:
        print 'adddevice returned error', getErrorString(devId)

    print '\n\nId\tName'
    for i in range(getNumberOfdevices()):
        devId = getdeviceId(i)
        print devId, getName(devId), methods(devId)


    print 'Done with unit test'
