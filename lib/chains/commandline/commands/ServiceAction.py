from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command
from chains.commandline import InvalidParameterException
from chains.common import amqp

class CommandServiceAction(Command):
    def main(self, *args):
        """
        Send action to service

        @param serviceId string  Service UUID
        @param action   string  Action to send
        @param args     mixed   Arguments to pass to action
        @optional args
        """
        args = list(args)
        try:
            serviceId = args.pop(0)
            action = args.pop(0)
        except IndexError:
            raise InvalidParameterException('usage: service action <serviceId> <action> [args]')
        return self.rpc('%s%s.%s.%s' % (amqp.PREFIX_SERVICE, amqp.PREFIX_ACTION, serviceId, action), args)
