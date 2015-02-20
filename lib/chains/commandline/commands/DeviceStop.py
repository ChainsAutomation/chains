from chains.commandline.commands import Command

class CommandDeviceStop(Command):
    def main(self, deviceId):
        """ Stop device """
        return self.rpc('oa.main.stopDevice', [deviceId])
