from chains.commandline.commands import Command

class CommandDeviceConfig(Command):
    def main(self, deviceId):
        """ Dump device config """
        return self.rpc('oa.main.getDeviceConfig', [deviceId])
