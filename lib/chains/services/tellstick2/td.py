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
# from ctypes import c_int, c_ubyte, c_void_p, c_char_p, POINTER, string_at,\
from ctypes import c_int, c_void_p, c_char_p, \
    create_string_buffer, byref

debug = False

# platform specific imports and CFUNC definitions:
if (platform.system() == 'Windows'):
    # Windows
    from ctypes import windll, WINFUNCTYPE
    tdlib = windll.LoadLibrary('TelldusCore.dll')

    DEVICEFUNC = WINFUNCTYPE(None, c_int, c_int, c_char_p, c_int, c_void_p)
    DEVICECHANGEFUNC = WINFUNCTYPE(None, c_int, c_int, c_int, c_int, c_void_p)
    SENSORFUNC = WINFUNCTYPE(None, c_char_p, c_char_p, c_int, c_int, c_char_p, c_int, c_int, c_void_p)
    RAWDEVICEFUNC = WINFUNCTYPE(None, c_char_p, c_int, c_int, c_void_p)

else:
    # Mac
    if (platform.system() == 'Darwin'):
        from ctypes import cdll, CFUNCTYPE
        tdlib = cdll.LoadLibrary('/Library/Frameworks/TelldusCore.framework/TelldusCore')
    # Others; if not found, try adding the directory with the file to env var LD_LIBRARY_PATH
    else:
        from ctypes import cdll, CFUNCTYPE
        tdlib = cdll.LoadLibrary('libtelldus-core.so.2')

    # Make tdReleasString work on *BSD
    tdlib.tdReleaseString.argtypes = [c_void_p]
    tdlib.tdReleaseString.restype = None

    DEVICEFUNC = CFUNCTYPE(None, c_int, c_int, c_char_p, c_int, c_void_p)
    DEVICECHANGEFUNC = CFUNCTYPE(None, c_int, c_int, c_int, c_int, c_void_p)
    SENSORFUNC = CFUNCTYPE(None, c_char_p, c_char_p, c_int, c_int, c_char_p, c_int, c_int, c_void_p)
    RAWDEVICEFUNC = CFUNCTYPE(None, c_char_p, c_int, c_int, c_void_p)


# Device methods
TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_TOGGLE = 8
TELLSTICK_DIM = 16
TELLSTICK_LEARN = 32
TELLSTICK_EXECUTE = 64
TELLSTICK_UP = 128
TELLSTICK_DOWN = 256
TELLSTICK_STOP = 512
TELLSTICK_ALL = 0x3FF

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


# Sensor value types
TELLSTICK_TEMPERATURE = 1
TELLSTICK_HUMIDITY = 2
TELLSTICK_RAINRATE = 4
TELLSTICK_RAINTOTAL = 8
TELLSTICK_WINDDIRECTION = 16
TELLSTICK_WINDAVERAGE = 32
TELLSTICK_WINDGUST = 64


sensorValueTypeReadable = {TELLSTICK_TEMPERATURE: 'Temperature',
                           TELLSTICK_HUMIDITY: 'Humidity',
                           TELLSTICK_RAINRATE: 'Rain rate',
                           TELLSTICK_RAINTOTAL: 'Rain total',
                           TELLSTICK_WINDDIRECTION: 'Wind direction',
                           TELLSTICK_WINDAVERAGE: 'Wind average',
                           TELLSTICK_WINDGUST: 'Wind gust'
                           }
# Error codes
TELLSTICK_SUCCESS = 0
TELLSTICK_ERROR_NOT_FOUND = -1
TELLSTICK_ERROR_PERMISSION_DENIED = -2
TELLSTICK_ERROR_DEVICE_NOT_FOUND = -3
TELLSTICK_ERROR_METHOD_NOT_SUPPORTED = -4
TELLSTICK_ERROR_COMMUNICATION = -5
TELLSTICK_ERROR_CONNECTING_SERVICE = -6
TELLSTICK_ERROR_UNKNOWN_RESPONSE = -7
TELLSTICK_ERROR_SYNTAX = -8
TELLSTICK_ERROR_BROKEN_PIPE = -9
TELLSTICK_ERROR_COMMUNICATING_SERVICE = -10
TELLSTICK_ERROR_CONFIG_SYNTAX = -11
TELLSTICK_ERROR_UNKNOWN = -99

# Controller typedef
TELLSTICK_CONTROLLER_TELLSTICK = 1
TELLSTICK_CONTROLLER_TELLSTICK_DUO = 2
TELLSTICK_CONTROLLER_TELLSTICK_NET = 3

# Device changes
TELLSTICK_DEVICE_ADDED = 1
TELLSTICK_DEVICE_CHANGED = 2
TELLSTICK_DEVICE_REMOVED = 3
TELLSTICK_DEVICE_STATE_CHANGED = 4

# Change types
TELLSTICK_CHANGE_NAME = 1
TELLSTICK_CHANGE_PROTOCOL = 2
TELLSTICK_CHANGE_MODEL = 3
TELLSTICK_CHANGE_METHOD = 4
TELLSTICK_CHANGE_AVAILABLE = 5
TELLSTICK_CHANGE_FIRMWARE = 6

methodsSupportedDefault = 0

_callbackFuncs = {}


def getNumberOfDevices():
    return tdlib.tdGetNumberOfDevices()


def getDeviceId(i):
    return tdlib.tdGetDeviceId(int(i))


def getDeviceIdFromStr(s):
    try:
        id = int(s)
        devId = getDeviceId(id)
        return devId, getName(devId)
    except:
        pass

    for i in range(getNumberOfDevices()):
        if s == getName(getDeviceId(i)):
            return getDeviceId(i), s

    return -1, 'UNKNOWN'


def getName(id):
    getNameFunc = tdlib.tdGetName
    getNameFunc.restype = c_void_p

    vp = getNameFunc(id)
    cp = c_char_p(vp)
    s = cp.value

    tdlib.tdReleaseString(vp)

    return s


def methods(id, methodsSupported=None, readable=False):
    if methodsSupported is None:
        methodsSupported = methodsSupportedDefault

    methods = tdlib.tdMethods(id, methodsSupported)
    if readable:
        l = []
        for m in methodsReadable:
            if methods & m:
                l.append(methodsReadable[m])
        return ','.join(l)

    return methods


def turnOn(intDeviceId):
    return tdlib.tdTurnOn(intDeviceId)


def turnOff(intDeviceId):
    return tdlib.tdTurnOff(intDeviceId)


def bell(intDeviceId):
    return tdlib.tdBell(intDeviceId)


def dim(intDeviceId, level):
    return tdlib.tdDim(intDeviceId, level)


def up(intDeviceId):
    return tdlib.tdUp(intDeviceId)


def down(intDeviceId):
    return tdlib.tdDown(intDeviceId)


def stop(intDeviceId):
    return tdlib.tdStop(intDeviceId)


def learn(intDeviceId):
    return tdlib.tdLearn(intDeviceId)


def lastSentCommand(intDeviceId, methodsSupported=None, readable=False):
    if methodsSupported is None:
        methodsSupported = methodsSupportedDefault

    if readable:
        return methodsReadable.get(tdlib.tdLastSentCommand(intDeviceId, methodsSupported), 'UNKNOWN')

    return tdlib.tdLastSentCommand(intDeviceId, methodsSupported)


def lastSentValue(id_):
    func = tdlib.tdLastSentValue
    func.restype = c_char_p
    return func(id_)


def getErrorString(intErrorNo):
    getErrorStringFunc = tdlib.tdGetErrorString
    getErrorStringFunc.restype = c_void_p

    vp = getErrorStringFunc(intErrorNo)
    cp = c_char_p(vp)
    s = cp.value

    tdlib.tdReleaseString(vp)

    return s


def addDevice():
    return tdlib.tdAddDevice()


def removeDevice(intDeviceId):
    return tdlib.tdRemoveDevice(intDeviceId)


def setName(intDeviceId, chNewName):
    if not isinstance(chNewName, str):
        raise ValueError('chNewName needs to be a str')
    if not isinstance(intDeviceId, int):
        raise ValueError('intDeviceId needs to be an integer')

    return tdlib.tdSetName(intDeviceId, chNewName)


def getProtocol(intDeviceId):
    if not isinstance(intDeviceId, int):
        raise ValueError('intDeviceId needs to be an integer')

    tdGetProtocolFunc = tdlib.tdGetProtocol
    tdGetProtocolFunc.restype = c_void_p

    vp = tdGetProtocolFunc(intDeviceId)
    cp = c_char_p(vp)
    s = cp.value

    tdlib.tdReleaseString(vp)

    return s


def getModel(intDeviceId):
    if not isinstance(intDeviceId, int):
        raise ValueError('intDeviceId needs to be an integer')

    tdGetModelFunc = tdlib.tdGetModel
    tdGetModelFunc.restype = c_void_p

    vp = tdGetModelFunc(intDeviceId)
    cp = c_char_p(vp)
    s = cp.value

    tdlib.tdReleaseString(vp)

    return s


def getDeviceParameter(intDeviceId, strName, defaultValue):
    if not isinstance(intDeviceId, int):
        raise ValueError('intDeviceId needs to be an integer')
    if not isinstance(strName, str):
        raise ValueError('strName needs to be a str')
    if not isinstance(defaultValue, str):
        raise ValueError('defaultValue needs to be a str')

    tdGetDeviceParameterFunc = tdlib.tdGetDeviceParameter
    tdGetDeviceParameterFunc.restype = c_void_p

    vp = tdGetDeviceParameterFunc(intDeviceId, strName, defaultValue)
    cp = c_char_p(vp)
    s = cp.value

    tdlib.tdReleaseString(vp)

    return s


def init(defaultMethods=0):
    # defaultMethods could be one or many from: TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN | TELLSTICK_EXECUTE | TELLSTICK_UP | TELLSTICK_DOWN | TELLSTICK_STOP
    global methodsSupportedDefault
    methodsSupportedDefault = defaultMethods
    tdlib.tdInit()


def close():
    tdlib.tdClose()


callbacks = {'lastAdd': 0,
             'deviceEvent': {},
             'deviceChangeEvent': {},
             'sensorEvent': {},
             'rawDeviceEvent': {}
             }


def deviceEvent(deviceId, method, data, callbackId, context):
    if debug:
        print 'DeviceEvent'
        print 'deviceId:', deviceId
        print 'method:', method
        print 'data:', data
        print 'callbackId:', callbackId
        print 'context:', context

    for key in callbacks['deviceEvent']:
        f = callbacks['deviceEvent'][key]
        try:
            f(deviceId, method, data, callbackId)
        except:
            print 'Error calling registered callback for deviceEvent'
            if debug:
                raise


def deviceChangeEvent(deviceId, changeEvent, changeType, callbackId, context):
    if debug:
        print 'DeviceChangeEvent'
        print 'deviceId:', deviceId
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
        print 'protocol:', protocol
        print 'model:', model
        print 'id:', id
        print 'datatype:', dataType
        print 'value:', value
        print 'timestamp:', timestamp
        print 'callbackId:', callbackId
        print 'context:', context

    for key in callbacks['sensorEvent']:
        f = callbacks['sensorEvent'][key]
        try:
            f(protocol, model, id, dataType, value, timestamp, callbackId)
        except:
            print 'Error calling registered callback for sensorEvent'
            if debug:
                raise


def rawDeviceEvent(data, controllerId, callbackId, context):
    if debug:
        print 'RawDeviceEvent'
        print 'data:', data
        print 'controllerId:', controllerId
        print 'callbackId:', callbackId
        print 'context:', context

    for key in callbacks['rawDeviceEvent']:
        f = callbacks['rawDeviceEvent'][key]
        try:
            f(data, controllerId, callbackId)
        except:
            print 'Error calling registered callback for rawDeviceEvent'
            if debug:
                raise


device_func = DEVICEFUNC(deviceEvent)
_callbackFuncs['device'] = device_func

deviceChange_func = DEVICECHANGEFUNC(deviceChangeEvent)
_callbackFuncs['deviceChange'] = deviceChange_func

sensor_func = SENSORFUNC(sensorEvent)
_callbackFuncs['sensor'] = sensor_func
    
rawDevice_func = RAWDEVICEFUNC(rawDeviceEvent)
_callbackFuncs['raw'] = rawDevice_func


def registerEvent(func, eventType):

    global callbacks
    if len(callbacks[eventType]) == 0:
        # if first registration of this type of callback
        # register the handler
        if eventType == 'deviceEvent':
            _callbackFuncs['deviceCallbackId'] = tdlib.tdRegisterDeviceEvent(_callbackFuncs['device'], 0)
        elif eventType == 'deviceChangeEvent':
            _callbackFuncs['deviceChangeCallbackId'] = tdlib.tdRegisterDeviceChangeEvent(_callbackFuncs['deviceChange'], 0)
        elif eventType == 'sensorEvent':
            _callbackFuncs['sensorCallbackId'] = tdlib.tdRegisterSensorEvent(_callbackFuncs['sensor'], 0)
        elif eventType == 'rawDeviceEvent':
            _callbackFuncs['rawCallbackId'] = tdlib.tdRegisterRawDeviceEvent(_callbackFuncs['raw'], 0)
        else:
            print 'Unknown event type', eventType

    callbacks[eventType][callbacks['lastAdd']] = func

    id = callbacks['lastAdd']
    callbacks['lastAdd'] += 1

    return id


def registerDeviceEvent(func):
    return registerEvent(func, 'deviceEvent')


def registerDeviceChangedEvent(func):
    return registerEvent(func, 'deviceChangeEvent')


def registerSensorEvent(func):
    return registerEvent(func, 'sensorEvent')


def registerRawDeviceEvent(func):
    return registerEvent(func, 'rawDeviceEvent')


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

    elif callbackId in callbacks['rawDeviceEvent']:
        del callbacks['rawDeviceEvent'][callbackId]
        if len(callbacks['rawDeviceEvent']) == 0:
            tdlib.tdUnregisterCallback(_callbackFuncs['rawCallbackId'])
            del _callbackFuncs['rawCallbackId']


def setProtocol(intDeviceId, strProtocol):
    return tdlib.tdSetProtocol(intDeviceId, strProtocol)


def setModel(intDeviceId, strModel):
    return tdlib.tdSetModel(intDeviceId, strModel)


def setDeviceParameter(intDeviceId, strName, strValue):
    return tdlib.tdSetDeviceParameter(intDeviceId, strName, strValue)


# Completly untested calls
def connectTellStickController(vid, pid, serial):
    tdlib.tdConnectTellStickController(vid, pid, serial)


def disconnectTellStickController(vid, pid, serial):
    tdlib.tdDisConnectTellStickController(vid, pid, serial)


# Missing support for these API calls:
#
# int tdRegisterControllerEvent( TDControllerEvent eventFunction, void *context);
# int tdSendRawCommand(const char *command, int reserved);    
#    TELLSTICK_API void WINAPI tdConnectTellStickController(int vid, int pid, const char *serial);
#    TELLSTICK_API void WINAPI tdDisconnectTellStickController(int vid, int pid, const char *serial);
#
#    TELLSTICK_API int WINAPI tdController(int *controllerId, int *controllerType, char *name, int nameLen, int *available);
#    TELLSTICK_API int WINAPI tdControllerValue(int controllerId, const char *name, char *value, int valueLen);
#    TELLSTICK_API int WINAPI tdSetControllerValue(int controllerId, const char *name, const char *value);
#    TELLSTICK_API int WINAPI tdRemoveController(int controllerId);


class Sensor(object):

    def __init__(self, protocol, model, id, dataType, value, timestamp):
        self.protocol = protocol
        self.model = model
        self.id = id
        self.dataType = dataType
        self.value = value
        self.timestamp = timestamp

    def __repr__(self):
        return "Sensor: %s.%s.%s %s value: %s %s" % (self.protocol, self.model, self.id, self.dataType, self.value, self.timestamp)

#    TELLSTICK_API int WINAPI tdSensor(char *protocol, int protocolLen, char *model, int modelLen, int *id, int *dataTypes);
#    TELLSTICK_API int WINAPI tdSensorValue(const char *protocol, const char *model, int id, int dataType, char *value, int len, int *timestamp);


def getSensors():
    """ returns all sensors in an array """
    sensors = []
    LEN = 256
    protocol = create_string_buffer(LEN)
    model = create_string_buffer(LEN)
    id_ = c_int()
    dataTypes = c_int()
    while 0 == tdlib.tdSensor(protocol, LEN, model, LEN, byref(id_), byref(dataTypes)):
        for i in range(0, 32):
            dataType = 1 << i
            if dataTypes.value & dataType:
                valuelen = c_int(256)
                value = create_string_buffer(256)
                timestamp = c_int()
                tdlib.tdSensorValue(protocol, model, id_, dataType, value, valuelen, byref(timestamp))
                sensors.append(Sensor(protocol.value, model.value, id_.value, dataType, value.value, timestamp.value))
    return sensors


if __name__ == '__main__':
    def cb(data, controllerId, callbackId):
        print 'RawDeviceEvent'
        print '  data:', data
        print '  controllerId:', controllerId
        print '  callbackId:', callbackId
        # print '  context:', context

    registerRawDeviceEvent(cb)
    import time
    while True:
        time.sleep(0.5)

if __name__ == 'x__main__':
    import time

    init(defaultMethods=TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN)

    print 'getNumberOfDevices', getNumberOfDevices()

    print 'Id\tName'
    for i in range(getNumberOfDevices()):
        devId = getDeviceId(i)
        print devId, getName(devId), methods(devId)

    if 0:
        print 'Methods(1)', methods(1)
        print 'methods(1, readable=True)', methods(1, readable=True)
        print 'methods(3124, readable=True)', methods(3124, readable=True)
        print 'TurnOn(1)', turnOn(1)
        time.sleep(1)
        print 'TurnOff(1)', turnOff(1)
        time.sleep(1)
        print 'Dim (1, 121)', dim(1, 121)

        print 'LastSentCommand(1)', lastSentCommand(1)
        print 'LastSentValue(1)', lastSentValue(1)
        print 'GetErrorString(-2)', getErrorString(-2)

    print 'getDeviceIdFromStr', getDeviceIdFromStr('2')
    print 'getDeviceIdFromStr', getDeviceIdFromStr('Vardagsrum')
    print 'getDeviceIdFromStr', getDeviceIdFromStr('234')

    devId = addDevice()
    if devId > 0:
        print 'AddDevice', devId
        print 'setName', repr(setName(devId, 'Test'))
        print 'getName', repr(getName(devId))
        print 'getProtocol', getProtocol(devId)
        print 'setProtocol', setProtocol(devId, 'arctech')
        print 'getProtocol', getProtocol(devId)

        print 'getModel', getModel(devId)
        print 'setModel', setModel(devId, 'selflearning-switch')
        print 'getModel', getModel(devId)

        print 'getDeviceParameter (unit)', repr(getDeviceParameter(devId, "unit", ""))
        print 'setDeviceParameter (unit)', repr(setDeviceParameter(devId, 'unit', '123'))
        print 'getDeviceParameter (unit)', repr(getDeviceParameter(devId, "unit", ""))

        print 'getDeviceParameter (house)', repr(getDeviceParameter(devId, "house", ""))
        print 'setDeviceParameter (house)', repr(setDeviceParameter(devId, "house", "321"))
        print 'getDeviceParameter (house)', repr(getDeviceParameter(devId, "house", ""))

        print '\n\nId\tName'
        for i in range(getNumberOfDevices()):
            devId = getDeviceId(i)
            print devId, getName(devId), methods(devId)

        print 'Remove Device', removeDevice(devId)

    else:
        print 'addDevice returned error', getErrorString(devId)

    print '\n\nId\tName'
    for i in range(getNumberOfDevices()):
        devId = getDeviceId(i)
        print devId, getName(devId), methods(devId)


    print 'Done with unit test'
