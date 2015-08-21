from chains.commandline.commands import Command
from chains.commandline import InvalidParameterException

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
        return self.rpc('da.%s.%s' % (serviceId, action), args)
