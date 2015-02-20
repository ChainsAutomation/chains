from chains.commandline.commands import Command

class CommandAmqpEvent(Command):
    def main(self, deviceId, key, value):
        """ Inject an event on message bus """
        event = {'device': deviceId, 'key': key, 'data': {'value':value}}
        self.connection.producer(queuePrefix='chainsadmin-amqp-event').put('de.%s.%s' % (deviceId, key), event)
        return "Sent event: %s" % event
