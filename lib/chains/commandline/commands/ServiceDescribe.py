from chains.commandline.commands import Command
from chains.common import amqp

class CommandServiceDescribe(Command):
    def main(self, serviceId):
        """ Describe service actions and events """
        return self.rpc('%s%s.%s.describe' % (amqp.PREFIX_SERVICE, amqp.PREFIX_ACTION, serviceId), [])
