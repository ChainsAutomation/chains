from chains.commandline.commands import Command

class CommandServiceConfig(Command):
    def main(self, serviceId):
        """ Dump service config """
        return self.rpc('oa.main.getServiceConfig', [serviceId])
