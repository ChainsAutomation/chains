from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandManagerList(Command):
    def main(self):
        """ List managers """
        self.setFormatter('managerList')
        return self.rpc('oa.main.getManagers', [])
