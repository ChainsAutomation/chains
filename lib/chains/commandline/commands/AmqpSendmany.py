from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command
import time
import sys
from six.moves import range


class CommandAmqpSendmany(Command):
    def main(self, number=1000, dotEvery=10, numEvery=100):
        """ Flood message bus with events """
        print("Sending %s events, showing dot every %s" % (number, dotEvery))
        prod = self.connection.producer(queuePrefix='chainsadmin-amqp-sendmany')
        t = time.time()
        dotnum = 0
        numnum = 0
        for i in range(number):
            prod.put('test', i)
            if dotnum == dotEvery:
                sys.stdout.write('.')
                sys.stdout.flush()
                dotnum = 0
            if numnum == numEvery:
                sys.stdout.write('%s' % i)
                sys.stdout.flush()
                numnum = 0
            dotnum += 1
            numnum += 1
        print("\n")
        t = time.time() - t
        return 'Sent in %s sec, %s sec pr event, %s events pr sec' % (t, t / number, number / t)
