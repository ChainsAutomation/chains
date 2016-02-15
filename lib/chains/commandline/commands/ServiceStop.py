from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandServiceStop(Command):

    def main(self, serviceId):
        """ Stop service """
        return self.rpc('oa.main.stopService', [serviceId])

    def help(self):
        return """
            Stop one or more services

                $ chains service start <uuid>
                Stop a specific service by uuid

                $ chains service start tellstick
                Lookup uuid for service with name tellstick, at any manager, and start it

                $ chains service start tellstick.pi3
                Lookup uuid for service with name tellstick at manager pi3, and start it

                $ chains service start tellstick,sonos
                Stop multiple services

                $ chains service tellstick,pi3,sonos,5b9a3c8ba31341dbba465ee504862c76
                Combination of the above

                $ chains service start all
                Stop all services that are currently online

                $ chains service start forceall
                Stop *all* services, even those already offline
        """
