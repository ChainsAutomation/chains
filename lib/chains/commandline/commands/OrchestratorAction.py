from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command
from chains.commandline import InvalidParameterException
from chains.common import amqp

class CommandOrchestratorAction(Command):
    def main(self, *args):
        """
        Send action to orchestrator

        @param action   string  Action to send
        @param args     mixed   Arguments to pass to action
        @optional args
        """
        args = list(args)
        try:
            action = args.pop(0)
        except IndexError:
            raise InvalidParameterException('usage: orchestrator action <action> [args]')
        return self.rpc('%s%s.%s.%s' % (amqp.PREFIX_ORCHESTRATOR, amqp.PREFIX_ACTION, 'main', action), args)
