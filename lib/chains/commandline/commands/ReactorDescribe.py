from chains.commandline.commands import Command

class CommandReactorDescribe(Command):
    def main(self, reactorId):
        """ Desecribe reactor actions """
        self.setFormatter('daemonDescribe')
        return self.rpc('ra.%s.describe' % reactorId, [])
