from chains.commandline.formatter import Formatter
import time

class FormatterReactorList(Formatter):
    def main(self, result):
        fmt = '%-20s %-10s %s'
        ret = []
        ret.append( '-'*50 )
        ret.append( fmt % ('Reactor', 'Online', 'Last heartbeat') )
        ret.append( '-'*50 )
        for reactorId in result:
            values = [reactorId]
            if result[reactorId]['online']:
                values.append('Online')
            else:
                values.append('')
            if result[reactorId].has_key('heartbeat'):
                t = time.time()-float(result[reactorId]['heartbeat'])
                if t > (60*60):
                    values.append('about %s hours ago' % int(round(t/60/60)))
                elif t > 60:
                    values.append('about %s min ago' % int(round(t/60)))
                else:
                    values.append('%s sec ago' % int(round(t)))
            else:
                values.append('')
            ret.append( fmt % tuple(values) )
        return '\n'.join(ret)

