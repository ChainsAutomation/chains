from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandManagerDescribe(Command):
    def main(self, managerId):
        """ Describe manager actions """
        self.setFormatter('daemonDescribe')
        return self.rpc('ma.%s.describe' % managerId, [])
