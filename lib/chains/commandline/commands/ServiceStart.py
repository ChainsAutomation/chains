from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandServiceStart(Command):

    def main(self, serviceId):
        """ Start service """
        return self.rpc('oa.main.startService', [serviceId])

    def help(self):
        return """
            Start one or more services

                $ chains service start <uuid>
                Start a specific service by uuid

                $ chains service start tellstick
                Lookup uuid for service with name tellstick, at any manager, and start it

                $ chains service start tellstick.pi3
                Lookup uuid for service with name tellstick at manager pi3, and start it

                $ chains service start tellstick,sonos
                Start multiple services

                $ chains service tellstick,pi3,sonos,5b9a3c8ba31341dbba465ee504862c76
                Combination of the above

                $ chains service start all
                Start all services that are currently offline but configured to auto-start

                $ chains service start forceall
                Start *all* services, even those already running, and those without auto-start

                $ chains service start offline
                Start all services that are currently offline
        """
