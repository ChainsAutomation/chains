from __future__ import absolute_import
from __future__ import print_function
from chains.commandline.commands import Command

class CommandRuleCreate(Command):
    def main(self):
        self.setFormatter('Silent')
        print('from chains.reactor.definition import *')
        print('#from ruleconfig import *')
        print('')
        print('def rule(context):')
        print('    yield Event(service="x", key="x", data={})')
        print('    Action(service="x", action="x", params=[])')
        return None
