from chains.commandline import commands
from chains.common import utils, introspect
import os

def getCommands():
    result = {}

    for dir in commands.getCommandDirs():
        for file in os.listdir(dir):
            if file[0] == '_': continue
            file = file.split('.')
            if file[-1:][0] != 'py': continue
            file = '.'.join(file[:-1])

            section, command = utils.caseSplit(file)

            if not result.has_key(section):
                result[section] = []

            result[section].append(command)

    return result

def getSections():
    result = []
    for section in getCommands():
        result.append(section)
    result.sort()
    return result

def getSectionCommands(section):
    commands = getCommands()
    result = commands.get(section)
    result.sort()
    return result

def getCommandHelp(section, command):
    dic = commands.load(section, command)
    obj = dic[section][command]
    fun = getattr(obj, 'main')
    descr = introspect.describeMethod(fun)
    return descr

"""
def formatCommand(section, command, info):
    txtCommand = '%s.%s' % (section, command)

    txtArgs = ''
    for arg in info['args']:
        txtArgs += arg['key'] + ' '

    txtDescr = info['info']

    return '%-60s %s' % (txtCommand + ' ' + txtArgs, txtDescr)
"""


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'sections':
        print ' '.join(getSections())

