from chains.service import Service
from chains.log import log
from chains import config
import sys, subprocess, time, os, hashlib, random

class EspeakService(Service):

    def onCommand(self, cmd, args):
        txt = None
        if cmd == 'speak':
            txt = args[0]
        else:
            data = {}
            data['greet'] = [
                'hello', 'hi',
                '<p xml:lang="no">hallo i luken</p>',
                '<p xml:lang="no">god dag.</p>',
                '<p xml:lang="no">halla.</p>',
                '<p xml:lang="no"><emphasis>morn</emphasis> du.</p>',
            ]
            data['bye'] = [
                'bye', 'good bye',
                '<p xml:lang="no">chains det bra</p>',
                '<p xml:lang="no">vi ses</p>',
            ]
            txts = data[cmd]
            k = len(txts)+1
            while k > (len(txts)-1):
                k = int(round(random.random()*len(txts)))
            txt = txts[k]
        try:
            espeak(txt, config.getServiceDataPath(self.config['id']), self)
        except Exception, e:
            print traceback.format_exc(e)
            raise


def espeak(txt, tmp, obj=None):

    if not os.path.exists(tmp):
        os.makedirs(tmp)
    wav = '%s/%s.wav' % (tmp, hashlib.md5(txt).hexdigest())
    
    if not os.path.exists(wav): # or os.lstat(wav)[6] < 400: # ignore small files (bug)
        cmd = ['espeak', '-s', '140', '-w', wav, '-m', txt]
        #espeak -v mb-en1 -m | mbrola -e /usr/share/mbrola/en1/en1 - test.wav ; play test.wav
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        ret = proc.wait()
        if ret != 0: raise Exception('Command failed: %s | %s | %s' % (cmd, out, err))
    
        '''
        fn = '/tmp/espeakpy%s' % time.time()
        f = open(fn,'w')
        f.write(out)
        f.close()
        pa = None
        if obj: pa = config.getServiceSharePath(obj)
        else: pa = '/srv/chains/share/services/Espeak'
        cmd = ['mbrola', '-e', '%s/voices/en1/en1' % pa, fn, wav]
        print cmd
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        ret = proc.wait()
        if ret != 0: raise Exception('Command failed: %s | %s | %s' % (cmd, out, err))
        '''
    
    cmd = ['play', wav]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    ret = proc.wait()
    if ret != 0: raise Exception('Command failed: %s | %s | %s' % (cmd, out, err))

    print txt
    print wav

if __name__ == '__main__':
    import sys
    espeak('<p xml:lang="no">hallo i luken</p>', '/tmp/espeak')
