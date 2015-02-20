#!/usr/bin/env python

from chains.commandline import describe
import sys

def log(msg):
    fp = open('/tmp/jazz','a')
    fp.write('%s\n' % msg)
    fp.close()

def returnItems(values):
    print ' '.join(values)

if __name__ == '__main__':
    idx = int(sys.argv[1])
    args = sys.argv[3:]

    #log('idx: %s' % idx)
    #log('args: %s' % args)

    if idx == 1:
        sections = describe.getSections()
        if args:
            arg = args.pop(0)
            for section in sections:
                if section.find(arg) == 0:
                    returnItems([section])
        else:
            returnItems(sections)

    elif idx == 2:
        section = args.pop(0)
        commands = describe.getSectionCommands(section)
        if args:
            arg = args.pop(0)
            for command in commands:
                if command.find(arg) == 0:
                    returnItems([command])
        else:
            returnItems(commands)
        
