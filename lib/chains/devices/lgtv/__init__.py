from chains.device import Device
from chains.common import log, utils
import time, serial

# www.lg.com/us/commercial/documents/m3701c-ba-rs232c.pdf
# https://sites.google.com/site/brendanrobert/projects/bits-and-pieces/lg-tv-hacks
# https://sites.google.com/site/brendanrobert/projects/bits-and-pieces/lg-tv-hacks/drawing-on-the-osd

# 00-64 in hex = volume, contrast etc range
class LgRange:
    min = 0
    max = 99  # ie. 65 hex

class LgBool:
    pass

class LgTvDevice(Device):

    # Protocol spec for commands
    spec = [
        ('power',       'k', 'a', LgBool()),
        ('inputSelect', 'x', 'b', {
                'dtv_ant': '00', 
                'dtv_cable': '01',
                'analog_ant': '10',
                'analog_cable': '11',
                'av1': '20', 'av2': '21',
                'comp1': '40', 'comp2': '41',
                'pc': '60', 
                'hdmi1': '90', 'hdmi2': '91', 'hdmi3': '92', 'hdmi4': '93'
            }),
        ('aspectRatio', 'k', 'c', {
                '4:3': '01',
                '16:9': '02',
                'zoom': '04',
                'set_by_prog': '06',
                'just_scan': '09',
                'cinema_zoom1': '10', # .... cinema_zoom 2-15 also available
                'cinema_zoom16': '1F'
            }),
        ('screenMute', 'k', 'd', {
                'off': '00',     # mute off, i.e. picture and vid out on
                'picture': '01', # picture off
                'vid_out': '10'  # vid out off
            }),
        ('volumeMute', 'k', 'e', LgBool()),
        ('volume', 'k', 'f', LgRange()), # 00-64 hex = volume range
        ('contrast', 'k', 'g', LgRange()),
        ('brightness', 'k', 'h', LgRange()),
        ('color', 'k', 'i', LgRange()),
        ('tint', 'k', 'j', LgRange()),
        ('sharpness', 'k', 'k', LgRange()),
        ('osd', 'k', 'l', LgBool()),
        ('treble', 'k', 'r', LgRange()),
        ('bass', 'k', 's', LgRange()),
        ('balance', 'k', 't', LgRange()),
        ('colorTemp', 'k', 'u', LgRange()),
        ('backlight', 'm', 'g', LgRange()),
        ('autoConf', 'j', 'u', '01'), # find picture pos, minimize shaking
        # MORE: remote lock, energy save, channel tuning, channel add/del, send IR key
    ]

    def onInit(self):
        self.interval = self.config.getInt('interval')
        self.last     = {}
        self.channel  = self.config.get('channel')
        self.serial   = serial.Serial(
            self.config.get('serial.device'),
            self.config.get('serial.bps'),
            timeout=self.config.getInt('serial.timeout')
        )
        self.serial.setRtsCts(self.config.getBool('serial.flowcont'))

    def runAction(self, action, args):

        if action == 'sendRaw':
            return self.sercmd(args[0])
        if action == 'describe':
            return self.action_describe()

        access  = action[:3]                   # "get" or "set"
        element = utils.lcfirst(action[3:])    # f.ex. power, inputSelect, etc
        spec    = self.getSpecElement(element) # config from self.spec for element
        if access not in ['get', 'set'] or not spec:
            raise Exception('No such action: %s' % action)
        if access == 'get':
            arg = 'ff'
        else:
            arg = args[0]

        #log.info('Action: action=%s access=%s element=%s arg=%s spec=%s' % (action, access, element, arg, spec))

        params = [access]
        for v in spec:
            params.append(v)
        params.append(arg)

        result = self._onCommand(*params)

        if access == 'set':
            self.sendEvent(element, {'value': arg})

        return result

    def _onCommand(self, access, action, c1, c2, args, arg):
        #log.info('_onCommand action=%s c1=%s c2=%s args=%s arg=%s' % (action, c1, c2, args, arg))

        # Parse args
        if access == 'set':
            if type(args) == type({}):
                try:
                    arg = args[arg]
                except KeyError: 
                    raise Exception('Invalid argument for command %s: %s' % (action, arg))
            elif args.__class__ == LgRange:
                arg = int(arg)
                if arg not in range(LgRange.min, LgRange.max) and arg not in ['255',255]:
                    raise Exception('Out of range argument for command: %s: %s' % (action, arg))
                arg = hex(arg)[2:] # int to hex (without 0x prefix)
            elif args.__class__ == LgBool:
                #if arg == '255':
                #    arg = hex(255)[2:]
                #else:
                    arg = ('%s'%arg).lower()
                    if arg in ['1','01','on','true']:
                        arg = '01'
                    else:
                        arg = '00'
            else:
                arg = args

        # Run command
        # <Command1> <Command2> <SetID> <Data>
        # f.ex: k a 1 00 = turn off power
        # SetID is set in TV menu, 1 is default for new TVs, 0 is all TVs
        c = '%s%s %s %s' % (c1, c2, self.channel, arg)
        #log.info('Serial request: %s' % c)
        #res = self.sercmd(c)

        self.serial.write('%s\n' % c)
        #res = self.serial.readline()
        res = ''
        for i in range(1000):
            ch = self.serial.read(1)
            #log.info('Serial char: %s' % ch)
            res += ch
            if ch == 'x':
                break

        #log.info('Serial response: %s' % res)

        # Parse response
        # <Command2> <SetID> <OK/NG><Data>
        # NG indicates error response, data is then error code
        # OK indicates success, data is then value (i.e. same as DATA for write commands)
        if not res: 
            raise Exception('Got empty response from LGTV for cmd: %s' % c)
        raw = res
        res = res.split(' ')
        if len(res) < 3: 
            raise Exception('Got unknown response from LGTV: %s' % res)
        res.append( res[2][2:] )
        res[2] = res[2][:2]

        if res[0] != c2:
            raise Exception('Got unexpected response (command mismatch) from LGTV: %s' % res)
        if res[2] not in ['OK','NG']:
            raise Exception('Got unexpected response (status mismatch) from LGTV: %s' % res)

        if res[3][-1:] == 'x': # strip terminating x
            res[3] = res[3][:-1]

        # TV returned an error
        if  res[2] == 'NG':
            msgs = {
                '01': 'Illegal code',
                '02': 'Not supported function',
                '03': 'Wait more time'
            }
            msg = ''
            try:
                msg = msgs[res[3]]
            except KeyError:
                pass
            raise Exception('LGTV rejected (%s) command with code: %s, msg: %s, raw: %s' % (res[2], res[3], msg, raw))

        # Parse result
        resultValue = res[3]
        if type(args) == type({}):
            # Value to key if dict
            for k in args:
                if args[k] == resultValue:
                    resultValue = k
                    break
        elif args.__class__ == LgRange:
            # Hex to int
            resultValue = int(resultValue, 16)
        elif args.__class__ == LgBool:
            if resultValue == '01':
                resultValue = True
            elif resultValue == '00':
                resultValue = False
            else:
                raise Exception('Unknown resultValue for boolean: %s' % resultValue)
        return resultValue


    # Build description from spec
    def onDescribe(self):
        data = {
            'info': 'LG TV - works with LG 42LH4000 (and probably all others with a RS232 port?)',
            'actions': [],
            'events': []
        }
        for cfg in self.spec:
            cmd = cfg[0]
            args = cfg[3]
            values = None

            getCommand = {
                'info': 'Get %s' % cmd,
                'name': 'get%s' % utils.ucfirst(cmd),
                'args': []
            }

            setCommand = {
                'info': 'Set %s' % cmd,
                'name': 'set%s' % utils.ucfirst(cmd),
                'args': []
            }

            if type(args) == type({}):
                setCommand['args'].append({
                    'info':     'Value',
                    'default':  None,
                    'required': True,
                    'valid':    args.keys(),
                    'type':     'string'
                })
            elif args.__class__ == LgRange:
                setCommand['args'].append({
                    'info':     'Value (%s-%s)' % (LgRange.min,LgRange.max),
                    'default':  None,
                    'required': True,
                    'valid':    None,
                    'type':     'int'
                })
            elif args.__class__ == LgBool:
                setCommand['args'].append({
                    'info':     'Value',
                    'default':  None,
                    'required': True,
                    'valid':    None,
                    'type':     'boolean'
                })
            else:
                setCommand['args'].append({
                    'info':     'Value',
                    'default':  None,
                    'required': True,
                    'valid':    None,
                    'type':     'string'
                })

            #if cmd not in ['power']:
            #    data['actions'].append(cg)
            #data['actions'].append(cs)

            data['actions'].append(getCommand)
            data['actions'].append(setCommand)

        return data

    def getSpecElement(self, key):
        for item in self.spec:
            if item[0] == key:
                return item

