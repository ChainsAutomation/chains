from chains.commandline.commands import Command

class CommandServiceStop(Command):
    def main(self, serviceId):
        """ Stop service """
        return self.rpc('oa.main.stopService', [serviceId])
