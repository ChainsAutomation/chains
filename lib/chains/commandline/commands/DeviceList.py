from chains.commandline.commands import Command

class CommandDeviceList(Command):
    def main(self):
        """ List all devices """
        self.setFormatter('deviceList')
        return self.rpc('oa.main.getDevices', [])
