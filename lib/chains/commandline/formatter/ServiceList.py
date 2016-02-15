from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.formatter import Formatter
import time


class FormatterServiceList(Formatter):
    def main(self, result):
        fmt = '%-15s %-8s %-15s %-15s %s'
        ret = []
        ret.append('-' * 90)
        ret.append(fmt % ('Service', 'Online', 'Manager', 'Heartbeat', 'ID'))
        ret.append('-' * 90)
        for serviceId in result:
            item = result[serviceId]
            main = item.get('main')
            if not main:
                main = {}
            values = [main.get('name')]
            if item.get('online'):
                values.append('Online')
            else:
                values.append('')
            if main.get('manager'):
                values.append(main.get('manager'))
            else:
                values.append('')
            if item.get('heartbeat'):
                t = time.time() - float(item.get('heartbeat'))
                if t > (60 * 60):
                    values.append('about %s hours ago' % int(round(t / 60 / 60)))
                elif t > 60:
                    values.append('about %s min ago' % int(round(t / 60)))
                else:
                    values.append('%s sec ago' % int(round(t)))
            else:
                values.append('')
            values.append(main.get('id'))

            ret.append(fmt % tuple(values))
        return '\n'.join(ret)
