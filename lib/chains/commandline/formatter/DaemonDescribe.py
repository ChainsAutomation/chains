from chains.commandline.formatter import Formatter
from chains.common.utils import ucfirst
import time

class FormatterDaemonDescribe(Formatter):
    def main(self, result):
        ret = ''
        if result['info']:
            ret += 'Info:'
            ret += '\n  %s\n' % result['info']
        if result['actions']:
            ret += 'Actions:'
            ret += '\n'
            for item in result['actions']:
                info = item['info']
                if not info:
                    info = ucfirst(item['name'])
                ret += '\n  # %s' % info
                astr = ''
                for a in item['args']:
                    if astr != '':
                        astr += ', '
                    if a['type']:
                        astr += '(%s) ' % a['type']
                    #if a['required']:
                    #    astr += '*'
                    astr += a['key']
                    if a['default']:
                        astr += '=%s' % a['default']
                ret += '\n  %s(%s)' % (item['name'], astr)
                ret += '\n'
        if result['events']:
            ret += '\nEvents:'
            for ev in result['event']:
                ret += '\n  %s' % ev
        return ret

