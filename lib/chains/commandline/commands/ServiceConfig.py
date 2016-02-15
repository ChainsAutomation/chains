from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandServiceConfig(Command):
    def main(self, serviceId):
        """ Dump service config """
        return self.rpc('oa.main.getServiceConfig', [serviceId])
