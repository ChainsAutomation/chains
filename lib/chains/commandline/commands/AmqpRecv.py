from chains.commandline.commands import Command
import time

class CommandAmqpRecv(Command):
    def main(self, topic=None):
        """ Snoop on the rabbitmq message bus """
        key = topic
        breaktxt = "use ctrl-c to stop..."
        if key:
            print 'Listen for events: %s, %s' % (key, breaktxt)
            cons = self.connection.consumer([key], queuePrefix='chainsadmin-amqp-recv')
        else:
            print 'Listen for all events, %s' % (breaktxt)
            cons = self.connection.consumer(queuePrefix='chainsadmin-amqp-recv')
        try:
            while True:
                key, val, id = cons.get()
                t = time.strftime('%Y-%m-%d %H:%M:%S')
                if id:
                    print '%s - %s = %s  [%s]' % (t, key, val, id)
                else:
                    print '%s - %s = %s' % (t, key, val)
                cons.ack()
        except KeyboardInterrupt:
            pass
        finally:
            cons.close()
