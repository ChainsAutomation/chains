from chains.commandline.commands import Command

class CommandAmqpRpc(Command):
    def main(self, topic, value=None, timeout=15):
        """ Run an RPC call to a daemon """
        txt  = "Call: %s = %s (timeout: %s)\n" % (topic, value, timeout)
        result = self.rpc(topic, value, timeout=timeout)
        txt += "Result: %s" % (result,)
        return txt
