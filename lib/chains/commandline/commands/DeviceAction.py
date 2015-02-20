from chains.commandline.commands import Command
from chains.commandline import InvalidParameterException

class CommandDeviceAction(Command):
    def main(self, *args):
        """
        Send action to device

        @param deviceId string  Device UUID
        @param action   string  Action to send
        @param args     mixed   Arguments to pass to action
        @optional args
        """
        args = list(args)
        try:
            deviceId = args.pop(0)
            action = args.pop(0)
        except IndexError:
            raise InvalidParameterException('usage: device action <deviceId> <action> [args]')
        return self.rpc('da.%s.%s' % (deviceId, action), args)
