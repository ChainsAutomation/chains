from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command
from chains.commandline import InvalidParameterException

class CommandReactorAction(Command):
    def main(self, *args):
        """
        Run reactor action
        @param  reactorId  string  Reactor ID
        @param  action     string  Action
        @param  args       mixed   Args to pass to action
        @optional args
        """
        args = list(args)
        try:
            reactorId = args.pop(0)
            action = args.pop(0)
        except IndexError:
            raise InvalidParameterException('usage: reactor action <reactorId> <action> [args]')
        return self.rpc('ra.%s.%s' % (reactorId, action), args)
