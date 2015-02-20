from chains.commandline.commands import Command
from chains.commandline import InvalidParameterException

class CommandManagerAction(Command):
    def main(self, *args):
        """
        Run manager action
        @param  managerId  string  Manager ID
        @param  action     string  Action
        @param  args       mixed   Args to pass on to action
        @optional args
        """
        args = list(args)
        try:
            managerId = args.pop(0)
            action = args.pop(0)
        except IndexError:
            raise InvalidParameterException('usage: manager action <managerId> <action> [args]')
        return self.rpc('ma.%s.%s' % (managerId, action), args)
