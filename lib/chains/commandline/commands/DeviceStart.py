from chains.commandline.commands import Command

class CommandDeviceStart(Command):
    def main(self, deviceId):
        """ Start device """
        return self.rpc('oa.main.startDevice', [deviceId])
