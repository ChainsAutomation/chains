import os, imp
from chains.common import config, utils

def load(section=None, command=None):
    for dir in getCommandDirs():
        result = loadFromDir(section, command, dir)
        if result: return result

def loadFromDir(section, command, commandsDir):
    result = {}
    if section:
        section = utils.lcfirst(section)
    if command:
        command = utils.lcfirst(command)
    for f in os.listdir(commandsDir):
        if f[0] == '_' or f.split('.')[-1:][0] != 'py':
            continue
        f = f.split('.')[:1][0]
        if f == 'Help':
            continue
        tmp = utils.caseSplit(f, firstOnly=True)
        _section = tmp[0]
        _command = tmp[1]
        if section and section != _section:
            continue
        if command and command != _command:
            continue
        if not result.has_key(_section):
            result[_section] = {}
        result[_section][_command] = utils.newObject(
            pkgName = f,
            className = 'Command%s' % f,
            path = commandsDir + '/' + f + '.py'
        )
    return result

def getCommandDirs():
    dirs = []

    # If user has configured custom commands dir
    items = config.data('commandline')
    if items:
        for key in items:
            tmp = key.split('.')
            if len(tmp) == 2 and tmp[0] == 'commands':
                dirs.append( items[key] + '/commands' )

    # Build in commands
    dirs.append( config.get('libdir') + '/commandline/commands' )

    return dirs

class Command:
    def init(self, connection):
        self.formatter = 'generic'
        self.connection = connection
    def setFormatter(self, formatter):
        self.formatter = formatter
    def getFormatter(self):
        return self.formatter
    def close(self):
        self.connection.close()
    def rpc(self, *args):
        rpc = self.connection.rpc(queuePrefix='rpc-chains-admin')
        return rpc.call(*args)
    def help(self):
        return """
            No help available

            Be a sport and contribute by adding help to the command :)

              1. Locate the apropriate Command in /srv/chains/lib/chains/commandline/commands/
              2. Add a help description line this:

                 def help(self):
                     return '''
                         My help text
                     '''
        """

"""
if __name__ == '__main__':
    data = load()
    for section in data:
        print section
        for id in data[section]:
            print '  %s' % id
"""
