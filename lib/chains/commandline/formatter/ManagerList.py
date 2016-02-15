from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.formatter import Formatter
import time


class FormatterManagerList(Formatter):
    def main(self, result):
        # fmt = '%-20s %-10s %-10s %s'
        fmt = '%-20s %-10s %s'
        ret = []
        ret.append('-' * 60)
        # ret.append( fmt % ('Manager', 'Online', 'Services', 'Last heartbeat') )
        ret.append(fmt % ('Manager', 'Online', 'Last heartbeat'))
        ret.append('-' * 60)
        for managerId in result:
            values = [managerId]
            if result[managerId]['online']:
                values.append('Online')
            else:
                values.append('')
            # values.append( result[managerId]['services'] )
            if 'heartbeat' in result[managerId]:
                t = time.time() - float(result[managerId]['heartbeat'])
                if t > (60 * 60):
                    values.append('about %s hours ago' % int(round(t / 60 / 60)))
                elif t > 60:
                    values.append('about %s min ago' % int(round(t / 60)))
                else:
                    values.append('%s sec ago' % int(round(t)))
            else:
                values.append('')
            ret.append(fmt % tuple(values))
        return '\n'.join(ret)
