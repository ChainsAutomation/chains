from chains.commandline.commands import Command
from chains.common import amqp

class CommandAmqpEvent(Command):
    def main(self, serviceId, key, value):
        """ Inject an event on message bus """
        event = {'service': serviceId, 'key': key, 'data': {'value':value}}
        self.connection.producer(queuePrefix='chainsadmin-amqp-event').put('%s%s.%s.%s' % (
                amqp.PREFIX_SERVICE, amqp.PREFIX_EVENT,
                serviceId, key
            ), event)
        return "Sent event: %s" % event
