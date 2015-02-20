from chains.common import amqp
from chains.common import log
from chains.commandline import commands, formatter, describe
import chains.common.jsonlib as json
from optparse import OptionParser
import cmd, shlex, traceback, sys

def usage():
    return '''
usage: chains-admin [options] <section> <command> [id] [...args...]

sections and their commands:

''' + help() + '''

options:
    --raw       Print output in raw mode (i.e. do not format putput)
    --json      Print output in json mode
    '''

# Auto-generate help from comments in objects in commandline/commands/*
# Follows same structure as device action comments
def help():
    txt = ''
    for section in describe.getSections():
        txt += '%s\n' % section
        for command in describe.getSectionCommands(section):
            info = describe.getCommandHelp(section, command)
            args = ''
            for arg in info['args']:
                if arg['required']: args += '<'
                else: args += '['

                args += arg['key']

                if arg.get('default'):
                    args += '=%s' % arg['default']

                if arg['required']: args += '>'
                else: args += ']'
                args += ' '
            txt += '  %-13s %-50s %s\n' % (command, args, info['info'].strip())
        txt += '\n'
    txt += '%-15s %-50s %s\n' % ('shell', '', 'Start interactive shell')
    txt += '\n'
    return txt.strip()

def OLD_help():
    return '''
device
  list                                    List all devices with status (at online managers)
  describe <deviceId>                     Describe device actions and events
  start <deviceId>                        Start device
  stop <deviceId>                         Stop device
  #restart <deviceId>                     Restart device [todo]
  #reload <deviceId>                      Reload device config [todo]
  enable <deviceId>                       Enable device
  disable <deviceId>                      Disable device
  action <deviceId> <action> [args...]    Run device action
  config <deviceId>                       Dump device config

manager
  list                                    List all (online) managers
  describe <managerId>                    Describe manager actions
  reload <managerId>                      Reload manager config
  action <managerId> <action> [args...]   Run manager action

reactor
  list                                    List all (online) reactors
  describe <reactorId>                    Describe reactor actions
  action <reactorId> <action> [args...]   Run reactor action

amqp
  event <deviceId> <key> <value> [extra]
  rpc <topic> [data]                      Todo
  send <topic> [data]                     Todo
  recv [topics]                           Todo

shell                                     Start interactive shell
    '''.strip()


class ChainsCommandException(Exception):
    pass

class InvalidParameterException(ChainsCommandException):
    pass

def parse(_req):
    parser = OptionParser()
    parser.add_option('-r', '--raw', action='store_true', dest='raw', help='Output raw data (do not format it)')
    parser.add_option('-j', '--json', action='store_true', dest='json', help='Output data as json')
    (options, req) = parser.parse_args(_req)
    try:
        section = req[0]
    except IndexError:
        raise InvalidParameterException('Missing section')
    try:
        command = req[1]
    except IndexError:
        raise InvalidParameterException('Missing command')
    id = None
    args = []
    if len(req) > 2:
        id = req[2]
        args = [id]
        if len(req) > 3:
            for a in req[3:]:
                if a[0] in ['{', '[']:
                    a = json.decode(a)
                args.append(a)
    options.section = section
    options.command = command
    options.args = args
    return options

def getCommandObject(section, command):
    cmds = commands.load(section, command)
    if not cmds:
        return
    if not cmds.has_key(section):
        raise InvalidParameterException('No such section: %s' % section)
    if not cmds[section].has_key(command):
        raise InvalidParameterException('No such command: %s in section: %s' % (command, section))
    obj = cmds[section][command]
    obj.init(amqp.Connection())
    return obj

def main(req):
    opt = parse(req)
    obj = getCommandObject(opt.section, opt.command)
    if not obj:
        print 'No such command: %s %s' % (opt.section,opt.command)
        sys.exit(1)
    try:
        result = obj.main(*opt.args)
        if opt.json:
            fmt = formatter.load('json')
        elif opt.raw:
            fmt = formatter.load('generic')
        else:
            fmt = formatter.load(obj.getFormatter()) 
        if not opt.json:
            print ''
        result = fmt.main(result)
        if result: print result
        if not opt.json:
            print ''
    finally:
        obj.close()

def shell():
    chainsCmd = ChainsCmd()
    chainsCmd.cmdloop()

class ChainsCmd(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "[chains] >> "
        self.intro  = "Welcome to to the Chains interactive console"

    def parseline(self, line):
        ret = cmd.Cmd.parseline(self, line)
        return ('main', ret[0] + ' ' + ret[1], ret[2])

    def do_main(self, line):
        if line == 'shell':
            print "Cannot start shell inside shell"
        else:
            args = shlex.split(line)
            if args[0] in ['exit','quit','EOF']:
                if args[0] == 'EOF':
                    print ''
                return True
            elif args[0] == 'help':
                print ''
                print help()
                print ''
            else:
                try:
                    main(args)
                except InvalidParameterException, e:
                    print "Invalid command: %s" % line
                except Exception, e:
                    print ''
                    traceback.print_exc()
                    print ''

if __name__ == '__main__':
    log.level = 'warn'
    #log.level = 'debug'
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == 'shell':
        shell()
    else:
        try:
            main(sys.argv[1:])
        except InvalidParameterException, e:
            if len(sys.argv) > 1:
                print ''
                print '%s' % e
            print usage()
