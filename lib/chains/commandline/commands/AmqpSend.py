from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandAmqpSend(Command):
    def main(self, topic, value=None):
        """ Inject a raw item to message bus """
        self.connection.producer(queuePrefix='chainsadmin-amqp-send').put(topic, value)
        return "Sent: %s = %s" % (topic,value)
