from chains.device import Device
from chains.log import log
from chains import utils

import alsaaudio, sys, time, os, wave

class AlsaDevice(Device):

    def _getSoundsPath(self):
        return '/srv/chains/data/devices/alsa' # @todo: from config

    def getMixer(self):
        try:
            return alsaaudio.Mixer(self.config['main']['mixer'])
        except KeyError:
            return alsaaudio.Mixer()

    def open(self):
        self.polldata = {'vol': -1, 'mute': -1}
        if self.poll():
            try: interval = float(self.config['main']['pollinterval'])
            except: interval = 1
            log.info('Starting poller with interval: %s' % interval)
            while True:
                time.sleep(interval)
                self.poll()
        else:
            log.info('Not starting poller')

    def poll(self):
        gotsome = False
        try:
            m = self.getMixer()
        except Exception, e:
            log.warn('Got no mixer: %s' % utils.e2str(e))
            return False
        try:
            vol = m.getvolume()[0]
            if vol != self.polldata['vol']:
                self.onEvent({'key': 'volume', 'value': vol})
                self.polldata['vol'] = vol
            gotsome = True
        except Exception, e:
            log.warn(utils.e2str(e))
        try:
            mut = m.getmute()[0]
            if mut != self.polldata['mut']:
                self.onEvent({'key': 'mute', 'value': mut})
                self.polldata['mut'] = mut
            gotsome = True
        except: pass
        return gotsome

    def onDescribe(self):
        return {
            'info': 'ALSA device',
            'commands': [
                ('play', [('sound','str'), ('soundset','str')], 'Play a sound file from soundset (or default soundset if none provided'),
                ('sounds', [('soundset','str')], 'List all sounds in a particular soundset (or default soundset if none provided'),
                ('sets', [], 'List all soundsets'),
                ('getVolume', []),
                ('getMute', []),
                ('setVolume', [('level','int')], 'Set volume'),
                ('setMute', [('level','bool')], 'Set mute'),
                ('volumeUp', []),
                ('volumeDown', []),
                ('mixers', []),
            ],
            'events': []
        }

    def onCommand(self, cmd, args):
        if cmd == 'mixers':
            return alsaaudio.mixers()
        if cmd == 'play':
            if len(args) < 1 or not args[0]: raise Exception('Need 1-2 args: file [soundset]')
            file = args[0]
            set = self.config['main']['defaultsoundset']
            if len(args) > 1 and args[1]:
                set = args[1]
            f = '%s/%s/%s' % (self._getSoundsPath(), set, file)
            if not os.path.exists(f):
                raise Exception('No such file: %s' % f)
            w = wave.open(f)
            self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
            self.out.setchannels(w.getnchannels())
            self.out.setrate(w.getframerate())
            self.out.setformat(alsaaudio.PCM_FORMAT_S16_LE) # todo
            # The period size controls the internal number of frames per period.
            # The significance of this parameter is documented in the ALSA api.
            #out.setperiodsize(160)  
            self.out.setperiodsize(w.getnframes()) # maybe?
            data = open(f,'r').read()
            self.out.write(data)
            return True
        elif cmd == 'sounds':
            set = self.config['main']['defaultsoundset']
            if len(args) > 0 and args[0]:
                set = args[0]
            f = '%s/%s' % (self._getSoundsPath(), set)
            ret = []
            for file in os.listdir(f):
                ret.append(file)
            return ret
        elif cmd == 'sets':
            ret = []
            for file in os.listdir(self._getSoundsPath()):
                ret.append(file)
            return ret            
        elif cmd == 'setVolume':
            m = self.getMixer()
            v = int(args[0])
            m.setvolume(v)
            self.onEvent({'key': 'volume', 'value': m.getvolume()[0]})
        elif cmd == 'setMute':
            m = self.getMixer()
            v = False
            if ('%s'%args[0]) in ['1','True']: v = True
            m.setmute(v)
            self.onEvent({'key': 'mute', 'value': m.getmute()[0]})
        elif cmd == 'volumeUp' or cmd == 'volumeDown':
            m = self.getMixer()
            v = m.getvolume()[0]
            fact = 1
            if args and len(args) > 1 and args[1]: fact = int(args[1])
            if cmd == 'volumeUp': v = v + fact
            else: v = v - fact
            m.setvolume(v)
            check = m.getvolume()
            if check != v: # hack because skips some steps here and there(?)
                if cmd == 'volumeUp': v = v + fact
                else: v = v - fact
                m.setvolume(v)
            self.onEvent({'key': 'volume', 'value': m.getvolume()[0]})
            return m.getvolume()[0]
        elif cmd == 'getVolume':
            m = self.getMixer()
            return m.getvolume()[0]
        elif cmd == 'getMute':
            m = self.getMixer()
            return m.getmute()[0]
        else:
            raise Exception('Unknown command: %s' % cmd)
