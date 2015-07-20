#!/usr/bin/python

import sys, os, socket
import time, datetime

from threading import Thread
from chains.device import Device
from chains.log import Log
from chains.com.client import Client


class AsteriskDevice(Device):

    def init(self):
        self.reader = AsteriskReader(self)
        self.reader.setDaemon(True)
        pass

    def open(self):
        print "open"
        self.reader.start()
        pass

    def close(self):
        self.reader.stop = True
        pass

    def onEvent(self, key, value, extra):
        if value: value = value.strip()
        event = {
            'key':    key.strip(),
            'device': self.config['id'],
            'value':  value,
            'extra': extra
        }
        self.devDaemon.onEvent(event)

 

class AsteriskReader(Thread):

    def __init__(self, device):
        Thread.__init__(self)
        self.stop = False
        self.client = Client();
        self.device = device
        # config
        try:
            mnguser = self.device.config['main']['mnguser'] 
        except KeyError:
            mnguser = 'hadevice'
        try:
            mngpass = self.device.config['main']['mngpass'] 
        except KeyError:
            mngpass = ''
        try:
            mngip = self.device.config['main']['mngip'] 
        except KeyError:
            mngip = '127.0.0.1'
        try:
            mngport = self.device.config['main']['mngport'] 
        except KeyError:
            mngport = '5038'
        #  asterisk
        self.asterisk = Asterisk(mnguser, mngpass, mngip, mngport)
        self.debug = False

    def run(self):
        while not self.stop:
            self.reader()

    def reader(self):
        print "listener starting"
        while not self.stop:
            try:
                data = self.asterisk.msconn.recv(1024)
            except socket.error, err:
                print "\nManager Receive Error %d: %s\nExiting." % (err.args[0],err.args[1])
                if not data: break
            lines = data.split("\r\n")
            if self.debug:
                for line in lines:
                    if line:
                        Log.debug("ASTERISK: %s" % line)
            if lines[0].startswith('Event:'):
                self.asterisk.extradict = {}
                disc,astevent = lines[0].split(':')
                #print 'New event: ' + astevent
                for line in lines[1:len(lines)]:
                    if line == '':
                        break
                    elif line.rfind(':'):
                        akey = line[0:line.find(':')]
                        aval = line[line.find(':') + 2:]
                        # akey,aval = line.split(':')
                        akey.lstrip().rstrip()
                        aval.lstrip().rstrip()
                        self.asterisk.extradict[akey] = aval
                    else:
                        print "Error" + line
                aval = None # @todo: f.ex. CallerIDNum for Newchannel etc..
                if self.asterisk.extradict.has_key('Uniqueid'):
                    aval = self.asterisk.extradict['Uniqueid']
                self.cleanextra(self.asterisk.extradict)
                self.device.onEvent(astevent, aval, self.asterisk.extradict)

    def cleanextra(self, extra):
        import re
        pat = re.compile('(.*)-(.*)')
        for k in extra:
           if pat.match(k):
                k2 = k.replace('-', '')
                extra[k2] = extra[k]
                del extra[k]
 
#class Asterisk(Device):
class Asterisk():

    def __init__(self, username, passwd, ip='127.0.0.1', port=5038):
        self.mnguser = username
        self.mngpass = passwd
        self.mngip = ip
        self.mngport = int(port)
        self.extradict = {}
        self.agentstatusevents = {
            'Agentcallbacklogin': 'Agent callback login',
            'Agentcallbacklogoff': '',
            'AgentCalled': '',
            'AgentComplete': '',
            'AgentConnect': '',
            'AgentDump': '',
            'Agentlogin': '',
            'Agentlogoff': '',
            'QueueMemberAdded': '',
            'QueueMemberPaused': '',
            'QueueMemberStatus': '',
        }
        self.callstatusevents = {
            'Cdr': '',
            'Dial': '',
            'ExtensionStatus': '',
            'Hangup': '',
            'MusicOnHold': 'Occurs when a channel is placed on hold/unhold and music is played to the caller.',
            'Join': '',
            'Leave': '',
            'Link': 'Two voice channels are linked together and voice data exchange commences.',
            'MeetmeJoin': '',
            'MeetmeLeave': '',
            'MeetmeStopTalking': '',
            'MeetmeTalking': '',
            'MessageWaiting': '',
            'Newcallerid': '',
            'Newchannel': '',
            'Newexten': 'Asterisk bx function event',
            'ParkedCall': '',
            'Rename': '',
            'SetCDRUserField': '',
            'Unlink': '',
            'UnParkedCall': '',
        }
        self.logstatusevents = {
            'Alarm': '',
            'AlarmClear': '',
            'DNDState': '',
            'LogChannel': '',
            'PeerStatus': 'Is triggered whenever a peer registers/unregisters with asterisk',
            'Registry': 'Asterisk registers with a peer',
            'Reload': '',
            'Shutdown': '',
        }
        self.userstatusevents = {
            'UserEvent': '',
        }
        self.astevents = {}
        self.astevents.update(self.userstatusevents)
        self.astevents.update(self.logstatusevents)
        self.astevents.update(self.callstatusevents)
        self.astevents.update(self.agentstatusevents)

        try:
            self.msconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.msconn.connect((self.mngip,self.mngport))
        except socket.error, err:
            print "\nManager Connection Error %d: %s\nExiting." % (err.args[0],err.args[1])
        self.msconn.send("Action: Login\r\n")
        self.msconn.send("UserName: " + self.mnguser + "\r\n")
        self.msconn.send("Secret: " + self.mngpass + "\r\n\r\n");
        self.msconn.send("Action: Events\r\nEventmask: On\r\n\r\n")
    
    def listener(self,delay):
        print "listener starting"
        while True:
            try:
                data = self.msconn.recv(1024)
            except socket.error, err:
                print "\nManager Receive Error %d: %s\nExiting." % (err.args[0],err.args[1])
                if not data: break
            lines = data.split("\r\n")
            if lines[0].startswith('Event:'):
                self.extradict = {}
                disc,astevent = lines[0].split(':')
                #print 'New event: ' + astevent
                for line in lines[1:len(lines)]:
                    if line == '':
                        break
                    elif line.rfind(':'):
                        akey = line[0:line.find(':')]
                        aval = line[line.find(':') + 2:]
                        # akey,aval = line.split(':')
                        akey.lstrip().rstrip()
                        aval.lstrip().rstrip()
                        self.extradict[akey] = aval
                    #print 'key:' + akey +  ', value: ' + aval 
                    else:
                        print_event('Error', line)
                self.print_event(astevent, self.extradict)
            if lines[0].startswith('Response:'):
                print "response: %s" % lines[0] # tuba
            time.sleep(delay)

    def print_event(self,key, value):
        print "|%15s|%60s|" % (key, value)
        line = "|%15s|%60s|" % ("---------------", "------------------------------------------------------------")
        print line


def main():
    import getopt, sys
    mnguser = 'hadevice'
    mngpass = 'banan123'
    mngip = '127.0.0.1'
    mngport = 5038
    # print "I was not imported"
    def usage():
        print sys.argv[0] + ' [--help | --verbose | --listen <polldelay>]'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvl:", ["help","verbose","listen"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
           usage()
           sys.exit(0)
        elif o in ("-l", "--listen"):
            test = Asterisk(mnguser, mngpass, mngip, mngport)
            test.listener(float(a))
        elif o in ("-v", "--verbose"):
            print 'verbose'


if __name__ == "__main__":
    main()
else:
    print "I was imported"
    print __name__

