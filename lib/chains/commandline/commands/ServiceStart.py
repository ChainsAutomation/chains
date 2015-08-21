from chains.commandline.commands import Command

class CommandServiceStart(Command):
    def main(self, serviceId):
        """ Start service """
        return self.rpc('oa.main.startService', [serviceId])
