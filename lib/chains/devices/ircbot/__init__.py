#! /usr/bin/env python
# encoding: utf-8
# based on
# example program using ircbot.py by Joel Rosdahl <joel@rosdahl.net>

# ircbot
try:
    from irc.bot import SingleServerIRCBot
    #from ircbot import SingleServerIRCBot
    from irc.client import is_channel, ip_quad_to_numstr, ip_numstr_to_quad, NickMask
    from irc.strings import lower as irc_lower
    #from irclib import nm_to_n, nm_to_h, nm_to_u, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr, is_channel
except:
    log.warn('Missing irc-library, time to fail')
from string import lower
from threading import Thread
import time
import datetime
## chains
from chains.device import Device
from chains.common import log

# Uncomment to log all server communication
#import irclib
#irclib.DEBUG = 1

ircC = {
    "BLACK": u"\x0301",
    "BLUE": u"\x0312",
    "TEAL": u"\x0310",
    "CYAN": u"\x0311",
    "MAGENTA": u"\x0313",
    "PURPLE": u"\x0306",
    "YELLOW": u"\x0308",
    "GREEN": u"\x0303",
    "ORANGE": u"\x0307",
    "RED": u"\x0304",
    "GRAY_DARK": u"\x0314",
    "GRAY_LIGHT": u"\x0315",
    "MARRO": u"\x0305",
    "BLAU_FOSC": u"\x0302",
    "VERD": u"\x0309",
    "BLANC": u"\x0300",
    "NORMAL": u"\x0f",
    "BOLD": u"\x02",
    "UNDERLINE": u"\x1f",
    "REVERSE": u"\x16",
}


def now():
    return datetime.datetime.now()


class IrcbotDevice(Device, SingleServerIRCBot):
    ''' IRC device '''
    #def __init__(self, channel, nickname, logfile, server, port=6667, secret=''):
    def onInit(self):

        # Channel(s) from config
        defaultChannel = 'chains'
        channels = []
        try:
            channels = self.config['main']['channel'].split(',')
        except KeyError:
            pass
        if not channels:
            channels = ['chains']
            log.warn('Missing or empty "channel" in %s device config, using %s' % (self.config['id'], defaultChannel))
        for i in range(len(channels)):
            channels[i] = self.addChannelPrefix(channels[i].strip())

        # Secret(s)
        secrets = {}
        for k in self.config['main']:
            tmp = k.split('.')
            if len(tmp) == 2 and tmp[0] == 'secret':
                secret[tmp[1]] = self.config['main'][k]

        # Nick
        nickname = 'chainsbot'
        try:
            nickname = self.config['main']['nickname']
        except KeyError:
            log.warn('No "nickname" in %s device config, using %s' % (self.config['id'], nickname))

        # Realname
        realname = 'chainsbot'
        try: realname = self.config['main']['realname']
        except KeyError:
            realname = nickname
            log.info('No "realname" in %s device config, using nickname: %s' % (self.config['id'], nickname))

        # Server
        server = 'localhost'
        try: server = self.config['main']['server']
        except KeyError:
            log.warn('No "server" in %s device config, using %s' % (self.config['id'], server))

        # Port
        port = 6667
        try: port = int(self.config['main']['port'])
        except KeyError:
            log.warn('No "port" in %s device config, using %s' % (self.config['id'], str(port)))

        def onStart(self):
        # For handelig async stuff
        self.waitEvents = {}

        SingleServerIRCBot.__init__(self, [(server, port)], nickname, realname)
        self.allChannels = channels
        self.channel = channels[0] # first chan is default chan
        log.info('all configured channels: %s' % self.allChannels)
        log.info('configured main channel: %s' % self.channel)
        self.secrets = secrets
        self.help_hash = {'help':('This menu',{}),
                        }
        self.queue = OutputManager(self.connection, .9)
        self.queue.start()
        try:
            self.start()
        except KeyboardInterrupt:
            self.connection.quit("Ctrl-C at console")
            print "Quit IRC."
        except Exception, e:
            self.connection.quit("%s: %s" % (e.__class__.__name__, e.args))
        raise
#
### chains stuff
    def onDescribe(self):
        return {
            'info': '',
            'commands': [
                ('pubmsg', [('message','str'), ('channel','str','(Optional)')]),
                ('privmsg', [('nick','str'),('message','str')]),
                ('join', [('channel','str'), ('secret','str','(Optional)')]),
                ('leave', [('channel','str','Channel (string) or channels (array) to leave')]),
                ('op', [('nick','str'), ('channel','str','(Optional, default is default/main channel)')]),
                ('whois', [('nick','str')]),
                #   Simple: ('mycommand', [('arg1','str'), ('arg2','int')])
                # Advanced: ('mycommand', [('arg1','str',None,'Arg1 - a string'), ('arg2','int',[3,4],'Arg2 - an int, either 3 or 4')], 'My command description')
            ],
            'events': [
                # ('myevent', ('key','str',['mykey1','mykey2'],'event.key = mykey1 or mykey2'), ('value','bool') ),
            ],
        }

    def action_op(self, nick, channel=None):
        if not channel: channel = self.channel
        channel = self.addChannelPrefix(channel)
        log.info('do_op1: %s' % channel)
        chanobj = None
        for cn, co in self.channels.items():
            if cn == channel:
                chanobj = co
                break
        if not chanobj:
            msg = 'Cannot op %s on %s because I am not joined to that channel' % (nick, channel)
            self.connection.notice(self.channel, msg)
            log.warn(msg)
            return
        if not self.connection.get_nickname() in chanobj.opers():
            msg = 'Cannot op %s on %s because I am not op on that channel' % (nick, channel)
            self.connection.notice(self.channel, msg)
            log.warn(msg)
            return
        cmd = '+o %s' % nick
        #log.info('do_op: MODE %s %s' % (channel,cmd))
        self.connection.mode(channel, cmd)

    def action_pubmsg(self, msg, channel=None):
        if not channel: channel = self.channel
        channel = self.addChannelPrefix(channel)
        msg = self.colorize(msg)
        self.queue.send(msg, channel)

    def action_privmsg(self, nick, msg):
        c = self.connection
        msg_pretty = self.colorize(msg)
        self.queue.send(msg_pretty,nick)

    def action_join(self, channel, secret=None, autoSecret=True):
        # Prefix channel with # if not already prefixed
        channel = self.addChannelPrefix(channel)
        # If no secret provided, check if channel has one configured in config
        if not secret and autoSecret:
            try: secret = self.secrets[channel]
            except KeyError: pass
        # Join channel with secret
        if secret:
            log.info('Joining channel %s with secret %s' % (channel, secret))
            self.connection.join(channel, secret)
        # Or without secret
        else:
            log.info('Joining channel %s without secret' % channel)
            self.connection.join(channel)

    def action_leave(self, channels):
        if type(channels) != type([]):
            channels = [channels]
        for i in range(len(channels)):
            channels[i] = self.addChannelPrefix(channels[i])
        log.info('Leave %s' % ','.join(channels))
        self.connection.part(channels)

    def on_nicknameinuse(self, c, e):
        data = {'key':'nicknameinuse', 'value':c.get_nickname(), 'extra': {} }
        self.botEvent(data)
        c.nick(c.get_nickname() + "_")
        data = {'key':'setnickname', 'value':c.get_nickname() + "_", 'extra': {} }
        self.botEvent(data)

    def on_welcome(self, c, e):
        for chan in self.allChannels:
            self.do_join(chan)

    def on_privmsg(self, c, e):
        nick = NickMask(e.source()).nick
        try:
            if e.arguments()[0][0] == '!':
                a2 = e.arguments()[0].split(" ")
                if len(a2[0][1:]) > 0:
                    self.command_switch(nick,e,a2[0][1:],a2[1:])
            else:
                a2 = e.arguments()[0].split(" ")
                data = {'key':'privmsg', 'value':e.arguments()[0], 'extra': {'nick':nick, 'type':e.eventtype(),'source':e.source(), 'target':e.target()}}
                #data = {'key':'privmessage', 'value':e.arguments()[0], 'extra': {'nick':nick}}
                self.botEvent(data)
        except Exception, e:
            self.say_private(nick, 'Exception: %s' % e)
            log.warn('Exception in on_privmsg: %s' % utils.e2str(e))

    def on_pubmsg(self, c, e):
        try:
            nick = NickMask(e.source()).nick
            a = e.arguments()[0].split(":", 1)
            #print "pub_msg: %s" % a
            #print "pub_msg first char: '%s'" % a[0][0]
            # parse first word as a command if pre'ed by <botname:>
            if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
                #self.command_switch(e, a[1].strip())
                a2 = e.arguments()[0].split(" ")
                if len(a2[0][1:]) > 0:
                    self.command_switch(nick,e,a2[1],a2[2:])
            # parse first word as a command if pre'ed by "!"
            elif e.arguments()[0][0] == '!':
                a2 = e.arguments()[0].split(" ")
                if len(a2[0][1:]) > 0:
                    self.command_switch(nick,e,a2[0][1:],a2[1:])
            # else: send as generic pubmessage event
            else:
                a2 = e.arguments()[0]
                data = {'key':'pubmessage', 'value':a2, 'extra': {'nick':nick}}
                self.botEvent(data)
            return
        except Exception, e:
            self.say_public('Exception in on_pubmsg: %s' % e)
            log.warn('Exception in on_privmsg: %s' % utils.e2str(e))

    # irclib.Event{ type=join, source=hafuzz!~hafuzz@193.91.144.150, target=#chains, arguments=[] }
    def on_join(self, c, e):
        nick = NickMask(e.source()).nick
        chan = e.target()
        log.info('on_join %s @ %s | %s' % (nick, chan, self.eventToString(e)))
        self.botEvent({
            'key': 'join',
            'value': nick,
            'extra': {'target': chan}
        })
        chan = self.delChannelPrefix(chan)
        greet_sect = 'greet_%s' % chan
        if self.config.has_key(greet_sect) and self.config[greet_sect].has_key(nick):
            msg = self.config[greet_sect][nick]
            self.say_public(msg, chan)
        op_sect = 'op_%s' % chan
        if self.config.has_key(op_sect) and self.config[op_sect].has_key(nick):
            tmp = e.source().split('!')
            ident, ip = tmp[1].split('@')
            if self.config[op_sect][nick] == ip:
                log.info('Op %s @ %s because ip matches config' % (nick, ip))
                self.do_op(nick, chan)
            else:
                log.info('Do not op %s @ %s because ip does not match config: %s' % (nick, ip, self.config[op_sect][nick]))
        if nick == self.connection.get_nickname():
            self.do_opme(chan)

    def say_public(self, text, channel=None):
        "Print TEXT into public channel, for all to see."
        log.info('say_public: %s | %s' % (text,channel))
        if not channel: channel = self.channel
        self.queue.send(text, self.addChannelPrefix(channel))

    def say_private(self, nick, text):
        "Send private message of TEXT to NICK."
        self.queue.send(text,nick)

    def reply(self, e, text):
        "Send TEXT to public channel or as private msg, in reply to event E."
        if e.eventtype() == "pubmsg":
            self.say_public("%s: %s" % (NickMask(e.source()).nick, text), e.target())
        elif e.eventtype() == "privmsg":
            self.say_private(NickMask(e.source()).nick, text)
        elif e.eventtype() == "dccmsg":
            self.connection.notice(NickMask(e.source()).nick, text)
        else:
            self.say_private(NickMask(e.source()).nick, text)

    def requests(self, nick, cmd, args):
        ret_result = []
        reqhead = ircC['BLUE'] + '[Request] ' + ircC['CYAN'] 
        reqtail = ircC['BLUE'] + ' [Request]'
        if cmd == 'request' or cmd == 'req':
            print "got request: %s" % args
            myreq = ' '.join(args[:])
            result = self.reqs_table.insert().execute(request=myreq, name=nick)
            print result
            return ['%s%s Added: %s%s' % (reqhead, ircC['NORMAL'],myreq, reqtail)]
        elif cmd == 'requests' or cmd == 'reqs':
            if len(args) == 0:
                print "got requests: %s" % args
                s = select([self.reqs_table]).order_by(func.random()).limit(5)
                result = s.execute()
                for row in result.fetchall():
                    ret_line = '%s %s%s %s(%s) %s[%s]' % (reqhead, row['request'], reqtail, ircC['YELLOW'],row['name'],ircC['RED'],row['id'])
                    ret_result.append(ret_line)
                return ret_result
            elif len(args) > 1:
                firstarg = lower(args[0])
                if firstarg == 'user':
                    print "finding reqs for specified user"
                    username = args[1]
                    s = select([self.reqs_table], self.reqs_table.c.name == username).order_by(func.random()).limit(5)
                    result = s.execute()
                    for row in result.fetchall():
                        ret_line = '%s %s%s %s(%s) %s[%s]' % (reqhead, row['request'], reqtail, ircC['YELLOW'],row['name'],ircC['RED'],row['id'])
                        ret_result.append(ret_line)
                    return ret_result
                elif firstarg == 'latest':
                    print "finding reqs for specified user"
                elif firstarg == 'oldest':
                    print "finding reqs for specified user"
                else:
                    return False
        elif cmd == 'reqfill' or cmd == 'requestfill':
            print "got reqfill: %s" % args
            # expecting args[0] = id, args[1] = delivername, if none, nick
        else:
            return ['man, you need %s!help request' % (ircC['BOLD'])]

    def quotes(self, nick, cmd, args):
        ret_result = []
        quotehead = ircC['BOLD'] + '[Quote] ' + ircC['CYAN'] 
        quotetail = ircC['NORMAL'] + ircC['BOLD'] + ' [Quote]'
        if cmd == 'quote' or cmd == 'q':
            #print self.quotes_table
            #s = select([self.quotes_table], self.quotes_table.qword == args[0])
            s = select([self.quotes_table], self.quotes_table.c.qword == args[0])
            result = s.execute()
            #print 'search quote: %s' % args[0]
            for row in result:
                print row
                ret_result.append('%s%s %s%s(%s) %s[%s]' % (quotehead, row['quote'], quotetail, ircC['YELLOW'], row['name'], ircC['RED'],row['id']))
            if (len(ret_result)) == 0:
                print [quotehead + "No such quote found" + quotetail]
                return [quotehead + "No such quote found" + quotetail]
            else:
                return ret_result
            #row = result.fetchone()
            #return row['quote']
        elif cmd == 'qadd':
            print "trying to add"
            myquote = ' '.join(args[1:])
            #i = insert([self.quotes_table], qword=args[0], quote=myquote, name=nick)
            #i = insert([self.quotes_table], self.quotes_table.c.qword=args[0], self.quotes_table.c.quote=myquote, self.quotes_table.c.name=nick)
            #print i
            #result = i.execute()
            result = self.quotes_table.insert().execute(qword=args[0], quote=myquote, name=nick)
            # result = self.quotes_table.insert().execute(self.quotes_table.c.qword=args[0], self.quotes_table.c.quote=myquote, self.quotes_table.c.name=nick)
            print result
            return ['%s[QUOTE]%s Added quote: %s' % (ircC['BOLD'],ircC['NORMAL'],args[0])]
        elif cmd == 'qdel' or cmd == 'qdelete':
            print "trying to delete %s" % args[0][0]
            #result = self.quotes_table.delete().execute(id==args[0][0])
            d = delete(self.quotes_table, self.quotes_table.c.id==args[0][0])
            result = d.execute()
            print result
            return ['%s[QUOTE]%s deleted quote: %s' % (ircC['BOLD'],ircC['NORMAL'],args[0])]
        elif cmd == 'qrand' or cmd == 'qrandom':
            print "trying to random quote"
            # s = select([self.quotes_table], self.quotes_table.c.qword == args[0])
            #s = select([self.quotes_table]).limit(1)
            print "functions:"
            print dir(func)
            s = select([self.quotes_table]).order_by(func.random()).limit(1)
            result = s.execute()
            #print result
            #print dir(result)
            row = result.fetchone()
            #print row
            ret_line = '%s: %s %s%s %s(%s) %s[%s]' % (row['qword'], quotehead, row['quote'], quotetail, ircC['YELLOW'],row['name'],ircC['RED'],row['id'])
            return [ret_line]
        else:
            return ['man, you need %s!help quote' % (ircC['BOLD'])]

    def addChannelPrefix(self, channel):
        if channel[0] == '#':
            return channel
        return '#' + channel

    def delChannelPrefix(self, channel):
        if channel[0] == '#':
            return channel[1:]
        return channel

    # =======================================
    # Stuff to handle async commands - start
    # =======================================

    # Start waiting for an event
    # Parameter 'key' should be something unique for the event.
    # F.ex. 'whois.<nick>' for a whois.
    # Because cannot wait for multiple events with same key simultaneously. 
    def waitEventStart(self, key):
        if self.waitEvents.has_key(key):
            raise Exception('Already waiting for event: %s' % key)
        log.info('waitEventStart: %s' % key)
        self.waitEvents[key] = {'data': {}, 'done': False}

    # An event we're (possibly) waiting for has occurred.
    # Add data.
    def waitEventAddData(self, key, data):
        log.info('waitEventAppendData: %s = %s' % (key, data))
        # Just ignore if we are not waiting for this event
        if not self.waitEvents.has_key(key):
            return
        # Add data
        for k in data:
            self.waitEvents[key]['data'][k] = data[k]

    # The event(s) we're waiting for have all occured,
    # so set a flag to signal that the data is ready to be fetched.
    def waitEventComplete(self, key):
        log.info('waitEventComplete: %s' % key)
        # Just ignore if we are not waiting for this event
        if not self.waitEvents.has_key(key):
            return
        self.waitEvents[key]['done'] = True

    # Actually wait for the events to occur
    # I.e. block untill the done flag is set and then return the data
    def waitEventWait(self, key, timeout=20):
        if not self.waitEvents.has_key(key):
            raise Exception('Not waiting for event: %s' % key)
        n = 0
        while 1:
            #log.info('waitEventWait: %s' % n)
            if self.waitEvents[key]['done']:
                data = self.waitEvents[key]['data']
                del self.waitEvents[key]
                return data
            n += 1
            if n > timeout:
                raise Exception('Exceeded timeout waiting for event: %s' % key)
            time.sleep(0.25)

    # =======================================
    # Stuff to handle async commands - end
    # =======================================

    def eventToString(self, e):
        return 'irclib.Event{ type=%s, source=%s, target=%s, arguments=%s }' % (e.eventtype(), e.source(), e.target(), e.arguments())


from threading import Thread, Event

class OutputManager(Thread):
    def __init__(self, connection, delay=.5):
        Thread.__init__(self)
        self.setDaemon(1)
        self.connection = connection
        self.delay = delay
        self.event = Event()
        self.queue = []

    def run(self):
        while 1:
            self.event.wait()
            while self.queue:
                msg,target = self.queue.pop(0)
                msg = msg.encode('utf-8')
                target = target.encode('utf-8')
                self.connection.privmsg(target, msg)
                time.sleep(self.delay)
            self.event.clear()

    def send(self, msg, target):
        self.queue.append((msg.strip(),target))
        self.event.set()

