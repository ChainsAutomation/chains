from chains.commandline.commands import Command

class CommandServiceDescribe(Command):
    def main(self, serviceId):
        """ Describe service actions and events """
        return self.rpc('da.%s.describe' % serviceId, [])
