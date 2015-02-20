from chains.commandline.commands import Command

class CommandDeviceDescribe(Command):
    def main(self, deviceId):
        """ Describe device actions and events """
        return self.rpc('da.%s.describe' % deviceId, [])
