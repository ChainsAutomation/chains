from chains.commandline.commands import Command

class CommandRuleCreate(Command):
    def main(self):
        self.setFormatter('Silent')
        print 'from chains.reactor.definition import *'
        print '#from ruleconfig import *'
        print ''
        print 'def rule(context):'
        print '    yield Event(device="x", key="x", data={})'
        print '    Action(device="x", action="x", params=[])'
        return None
