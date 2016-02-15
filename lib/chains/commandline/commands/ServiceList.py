from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandServiceList(Command):

    def main(self):
        """ List all services """
        self.setFormatter('serviceList')
        return self.rpc('oa.main.getServices', [])

    def help(self):
        return """
            List all services
        """
