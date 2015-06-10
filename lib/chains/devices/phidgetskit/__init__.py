import time
from Phidgets.PhidgetException import *
from Phidgets.Events.Events import *
from Phidgets.Devices.InterfaceKit import *

from chains.device import Device
from chains.common import log

def bint(arg):
    if type(arg) == type(True):
        if arg: return 1
        else: return 0
    elif type(arg) == type('') or type(arg) == type(u''):
        if arg == '1' or arg == 'True': return 1
        else: return 0
    elif type(arg) == type(1):
        if arg > 0: return 1
        else: return 0
    else:
        log.info('Unknown bint arg converted to 0: %s (%s)' % (arg, type(arg)))
        return 0

class PhidgetsKitDevice(Device):

    pmethods = [
        'getDeviceLabel', 'getDeviceName', 'getDeviceType', 
        'getDeviceVersion', 'getInputCount', 'getInputState', 
        'getLibraryVersion' , 'getOutputCount', 'getOutputState', 
        'getRatiometric', 'getSensorChangeTrigger', 'getSensorCount',
        'getSensorRawValue', 'getSensorValue', 'getSerialNum',
        'isAttached', 'setSensorChangeTrigger',
        'setRadiometric',
    ]

    # ==== Implementation of Device base ====

    def onInit(self):
        self.dev = InterfaceKit()
        self.setEventHandlers()

    def setThresholds(self):
        for k in [0,1,2,3,4,5,6,7]:
            val = None
            try:
                val = self.config.get('trigger%s' % k)
            except:
                pass
            if not val:
                continue
            self.dev.setSensorChangeTrigger(k, int(val))

    def onStart(self):
        try:
            serial = self.config.get('serial')
            if serial:
                serial = int(serial)
        except KeyError:
            pass
        if not serial:
            serial = -1
        try:
            log.info("Open Phidget with serial: %s" % serial)
            self.dev.openPhidget(serial)
            #self.dev.openPhidget()
            log.info("Waiting for Phidget to be attached...")
            self.dev.waitForAttach(100000)
            self.phidgetsId = self.dev.getSerialNum()
            log.info("Phidget with serial: %s attached" % self.phidgetsId)
            self.diginput = self.dev.getInputCount()
            log.info("Phidget %s has %s digital inputs" % (self.phidgetsId, self.diginput))
            self.digoutput = self.dev.getOutputCount()
            log.info("Phidget %s has %s digital outputs" % (self.phidgetsId, self.digoutput))
            self.analog = self.dev.getSensorCount()
            log.info("Phidget %s has %s analog inputs" % (self.phidgetsId, self.analog))
            self.ifname = self.dev.getDeviceName()
            log.info("Phidget %s has name: %s" % (self.phidgetsId, self.ifname))
            self.setThresholds()
                
        # make sure dev is closed again if error
        except PhidgetException, e:
            self.close()
            self.phidgetsId = None
            # but still let the exception continue down the stack
            # (and set code|message that are not seen with tostring for PE)
            raise Exception("PhidgetsException, code: %s, msg: %s" % (e.code, e.message))

    def onShutdown(self):
        #time.sleep(0.1) # hack for not responding when setting outputs just before close
        self.dev.closePhidget()

    def runAction(self, cmd, args):
        if cmd == 'setOutput':
            # arg 1 is f.ex. o2, we only want 2, as an int, not a string
            args[0] = int(args[0][1:])
            # arg 2 is 0 or 1, as int. but be forgiving (bint)
            if len(args) < 2:
                args.append(0)
            args[1] = bint(args[1])
            #log.info("setOutput ARGS: %s" % (args,))
            res = self.dev.setOutputState(args[0], args[1])
            log.debug("ifkit.setOutputState: %s, %s = %s" % (args[0], args[1], res))
        else:
            if cmd in self.pmethods:
                args2 = []
                for a in args:
                    try: a = int(a)
                    except: pass
                    args2.append(a)
                fun = getattr(self.dev, cmd)
                if fun: return fun(*args2)
            raise Exception('Unknown command: %s' % cmd)

    def isOpen(self):
        return self.dev.isAttached()

    def onDescribe(self):
        allinputs = ['i0','i1','i2','i3','i4','i5','i6','i7','i8','i9','i10','i11','i12','i13','i14','i5']
        allsensors = ['s0','s1','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','s12','s13','s14','s15']
        alloutputs = ['o0','o1','o2','o3','o4','o5','o6','o7','o8','o9','o10','o11','o12','o13','o14','o15']
        inputs = allinputs[:self.diginput]
        sensors = allsensors[:self.analog]
        outputs = alloutputs[:self.digoutput]
        events = []
        if sensors:
            sensorevents = ('sensorChange', ('key','str',sensors,'Sensor port'), ('value','int') )
            events.append(sensorevents)
        if inputs:
            inputevents = ('inputChange', ('key','str',inputs,'Input port'), ('value','bool') )
            events.append(inputevents)
        desc = {
            'info': self.ifname,
            #'info': self.dev.getDeviceLabel() + ' : ' + self.getDeviceType() + ' : ' + self.getDeviceName(),
            'commands': [
                ('setOutput', [('key','str',outputs,'Output port'), ('value','bool')], 'Set an input on/off')
            ],
            'events': events,
            'serial': self.phidgetsId,
            'analog_sensors': self.analog,
            'digital_inputs': self.diginput,
            'digital_outputs': self.digoutput
        }
        for f in self.pmethods:
            args = [] # todo
            desc['commands'].append((f, args, f))
        return desc

    # ==== Event handlers for PhidgetsEvents ====

    def onSensorChange(self, e):
        self._onEvent('sensor', e)
        return 0
    def onInputChange(self, e):
        self._onEvent('input', e)
        return 0
    def onOutputChange(self, e):
        self._onEvent('output', e)
        return 0

    def onAttach(self, e):
        log.debug("InterfaceKit attached: %i" % (e.device.getSerialNum()))
        self.sendEvent('status', {'value': 'attached'})
        self.setThresholds()
        return 0

    def onDetach(self, e):
        log.debug("InterfaceKit attached: %i" % (e.device.getSerialNum()))
        self.sendEvent('status', {'value': 'detached'})
        return 0

    def onError(self, e):
        log.error("Phidget Error %s: %s" % (e.eCode, e.description))
        return 0

    def _onEvent(self, type, e):
        pre = ''
        if type == 'sensor': pre = 's'
        elif type == 'input': pre = 'i'
        elif type == 'output': pre = 'o'
        else: raise Exception('Unknown type: %s' % type)
        key = '%s%s' % (pre,e.index)
        event = {}
        #event = {
        #    'key':    '%s%s' % (pre,e.index)
        #    #'device': self.config['id'],
        #}
        if type == 'sensor':
            event['value'] = e.value
            sensorType = self.config.get('type%s' % e.index)
            if sensorType:
                event['value'] = self.parseValue(event['value'], sensorType)
                event['type'] = sensorType
        else:
            event['value'] = e.state
        self.sendEvent(key, event)

    # ==== Helper functions =====

    def setEventHandlers(self):
        self.dev.setOnAttachHandler(self.onAttach)
        self.dev.setOnDetachHandler(self.onDetach)
        self.dev.setOnErrorhandler(self.onError)
        self.dev.setOnInputChangeHandler(self.onInputChange)
        self.dev.setOnOutputChangeHandler(self.onOutputChange)
        self.dev.setOnSensorChangeHandler(self.onSensorChange)

    def parseValue(self, value, type):
        if value == None:
            return None
        # Temperature - Celcius
        if type == 'temperature':
            return ( (float(value)/1000) * 222.22 ) - 61.111
        # Humidity - Relative humidity percent (RH%)
        elif type == 'humidity':
            return ( (float(value)/1000) * 190.6 ) - 40.2
        # Magnet - Gauss
        elif type == 'magnet':
            return 500 - value 
        # DC Current (DC amps)
        elif type == 'amp_dc':
            return ( (float(value)/1000) * 50 ) - 25
        # AC Current (RMS amps)
        elif type == 'amp_ac':
            return (float(value)/1000) * 27.75
        # Sonar distance (cm)
        elif type == 'sonar':
            return float(value) * 1.296
        elif type == 'ir5mm':
            val = 0
            if int(value) > 0:
                val = 1
            return val
