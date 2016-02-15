from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandReactorDescribe(Command):
    def main(self, reactorId):
        """ Desecribe reactor actions """
        self.setFormatter('daemonDescribe')
        return self.rpc('ra.%s.describe' % reactorId, [])
