from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command
from chains.common import amqp
import json, types

class CommandAmqpEvent(Command):
    def main(self, serviceId, device, key, data):
        """ Inject an event on message bus """

        if type(data) == types.DictType:
            data = data
        elif data[0] == '{':
            data = json.loads(data)
        else:
            data = {'test': {'value': data}}
        event = {'service': serviceId, 'device': device, 'key': key, 'data': data}
        self.connection.producer(queuePrefix='chainsadmin-amqp-event').put('%s%s.%s.%s' % (
                amqp.PREFIX_SERVICE, amqp.PREFIX_EVENT,
                serviceId, key
            ), event)
        return "Sent event: %s" % event
