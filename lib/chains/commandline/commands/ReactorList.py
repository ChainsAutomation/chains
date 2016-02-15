from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandReactorList(Command):
    def main(self):
        """ List reactors """
        self.setFormatter('reactorList')
        return self.rpc('oa.main.getReactors', [])
