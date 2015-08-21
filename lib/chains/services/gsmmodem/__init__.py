#!/usr/bin/python

# import string, os
# import sys
import sys, time, serial, re

from threading import Thread
from chains.service import Service
from chains.log import log
from chains.services.base.haserial import SerialService
from chains import utils


# @todo: encoding/decoding of special chars
#
# aa = \x0f
# ae = ?
# oe = ?
# what charset is the gsmmodem using?
#
# NB:
# - Special chars in received msgs converted to bogus(?)
# - Special chars in sent msgs cause msg not to be sent at all(!)

# @todo: concurrency issues
# - Reading incoming SMS'es and running actions won't occur at the same time (self.reading check).
# - But an SMS may arrive at any time, event if self.reading=True and we're running a function.
# - So we risk getting an incoming-sms-line in our command output (and subsequently miss that sms on next msg-poll)
# - Possible solution: Check all responses for sms-lines and send them if found.


class WaitTimeoutException(Exception):
    pass

class GsmModemService(SerialService):

    timeFormat = '%y/%m/%d,%H:%M:%S'
    smsStores = [
        ('read',    'REC READ'),
        ('unread',  'REC UNREAD'),
        ('sent',    'STO SENT'),
        ('unsent',  'STO UNSENT'),
        ('all',     'ALL')
    ]

    def open(self):
        self.reading = True                 # true when polling or running a function
                                            # (because should never do both at the same time!)
                                            # hm, it doesn't work after all, because incoming sms'es may appear anytime...
        self.msgqueue = []                  # received messages to be sent as events
        self.polldata = {}
        self.trySendPin()                   # send pin if in config and not sent already
        res = self.cmd("at+cmgf=1")         # set sms to text mode
        res = self.cmd("at+cnmi=2,1,0,0,1") # watch incoming messages
        res = self.cmd("at^sctm=1,1")       # enable presentation of urc and temperature
        self.reading = False

        while True:
            try:
                self.waitReading()
                self.setReading(True)
                log.debug('1. READ DATA')
                self.tryReadData()              # read incoming messages and add to queue
                log.debug('2. POLL DATA')
                self.pollData()                 # poll signal, temperature etc. and send events on change -- concurrency issues!
                log.debug('3. SEND SMS EVENTS')
                self.trySendSmsEvents()         # if any msgs found, lookup details and send events
                log.debug('4. ------------------------------------')
                self.setReading(False)
            except WaitTimeoutException:
                pass
            time.sleep(10)


    def cmd(self, cmd, bufsize=3, raw=False):
        # Serial explodes on unicode, so encode to utf8
        if type(cmd) == type(u''): cmd = cmd.encode('utf-8')

        # Run command
        ret = self.sercmd(cmd, bufsize=bufsize, tries=10, skipempty=True, returnList=True)

        # We may have an unrelated incoming SMS in the response
        hack = ret
        ret = []
        for l in hack:
            if not self.onReadData(l, quiet=True):
                ret.append(l)

        # Return raw line(s)
        if raw:
            return ret

        # Or return parsed first line
        try: ret = ret[0]
        except IndexError: return ''
        return self.parseResult(ret)


    def parseResult(self, data):
        pat = re.compile('\+([A-Z]+): (.+)')
        m = pat.match(data)
        if not m:
            #return None
            return ''
        pre = m.group(1)
        val = m.group(2)
        val = val.strip().strip('"')
        return val

    def trySendPin(self, force=None, pin=None):
        if not force:
            try:
                if not self.config['main']['sendpin']: return
            except KeyError:
                return
            res = self.cmd("at+cpin?")
            if res == '+CPIN: READY':
                return
        if not pin:
            try:
                pin = self.config['main']['pincode']
                if not pin: return
            except KeyError:
                return
        res = self.cmd("at+cpin=%s" % pin)
        log.info("Sent pin")

    def tryReadData(self):
        data = self.serial.readline()
        if data:
            self.onReadData(data)
            return True
        return False

    def setReading(self, reading):
        #log.info("setReading: %s" % reading)
        self.reading = reading

    def waitReading(self):
        #log.info("waitReading")
        n = 1
        max = 100
        while n < max:
            if not self.reading:
                return
            n += 1
            time.sleep(0.1)
        raise WaitTimeoutException('Timed out waiting for reading to stop')

    def trySendSmsEvents(self):
        while len(self.msgqueue) > 0:
            msgid = self.msgqueue.pop(0)
            msg = self.getSms(msgid)
            self.onSms(msg)

    def getSms(self, id):
        res0 = self.cmd('at+cmgr=%s' % id, bufsize=10, raw=True)
        res = res0[0]
        txt = res0[1]
        # fixme
        res = res.replace(',,',',"",')
        tmp = res.split('","')
        tmp[0] = tmp[0].replace('+CMGR: "', '')
        tmp2 = []
        for t in tmp:
            tmp2.append(t.strip(' ').strip('"'))
        # what is tmp[2] ? always empty? ##  ['+CMGR: "REC UNREAD","+4792489963",,"09/10/07,01:15:56+08"', 'D']
        res = {'status': tmp2[0], 'callerid': tmp2[1], 'time': tmp2[3], 'message': txt, 'id': id}
        log.info("getSms: %s: %s" % (id, res))
        return res

    def deleteSms(self, id):
        self.cmd('at+cmgd=%s' % id, bufsize=1) #, bufsize=10, raw=True)

    def onReadData(self, data, quiet=False):
        data = data.strip()
        if not data: return
        id = self.matchIncomingSms(data)
        if id:
            log.debug("Incoming sms: %s" % id)
            self.msgqueue.append(id)
            return True
        elif data and not quiet:
            log.debug("Ignored unknown in: %s" % data)
            return False

    def matchIncomingSms(self, data):
        pat = re.compile('\+CMTI: "MT",(\d+)')
        m = pat.match(data)
        if m:
            id = m.group(1)
            return id
        else:
            return None

    def onSms(self, sms):
        event = {
            'key':    'smsReceived',
            #'service': self.config['id'],
            'value':  sms['message']
        }
        del sms['message']
        event['extra'] = sms
        #self.devDaemon.onEvent(event)
        self.onEvent(event)
        if self.config['main'].has_key('delsmsonrecv') and self.config['main']['delsmsonrecv'] not in ['','0']:
            log.info('Delete received sms on event sent: %s' % sms['id'])
            self.deleteSms(sms['id'])

    def pollData(self):
        curr = self.pollDataGetCurrent()
        last = self.polldata
        for k in curr:
            if not last.has_key(k) or last[k] != curr[k]:
                self.onEvent({'key': k, 'value': curr[k]})
        self.polldata = curr

    def pollDataGetCurrent(self):
        data = {}
        tmp = self.cmd_getIndicators()
        for k in tmp:
            data[k] = tmp[k] 
        data['temperature'] = self.cmd_getTemperature()
        data['pinstatus'] = self.cmd_getPinStatus()
        return data

    def onCommand(self, cmd, args):
        self.waitReading()
        self.setReading(True)
        try: fun = getattr(self, 'cmd_%s' % cmd)
        except AttributeError: raise Exception('No such command: %s' % cmd)
        #self.cmdqueue.append((fun,args))
        res = fun(*args)
        self.setReading(False)
        return res

    def cmd_raw(self, cmd):
        return self.cmd(cmd, raw=True)

    """ # deprecated; use aliases for these instead. see onDescribe for listSms
    def cmd_listSmsStores(self):
        res = self.cmd('AT+CMGL=?', raw=True)
        res2 = res[0].split('CMGL: ')
        if len(res2) != 2:
            raise Exception('Unknown result: %s' % res)
        res2 = res2[1] #  ("REC UNREAD","REC READ","STO UNSENT","STO SENT","ALL")
        print 'res21: %s' % res2
        res2 = res2.strip()[2:-2] # REC UNREAD","REC READ","STO UNSENT","STO SENT","ALL
        print 'res22: %s' % res2
        res2 = res2.split('","')
        print 'res24: %s' % res2
        return res2
    """

    # Not finished!
    # +CMGL: <index>, <stat>, <oa>/<da>, [<alpha>], [<scts>][, <tooa>/<toda>, <length>]
    def cmd_listSms(self, store=None):
        realStore = None
        if store:
            for s in self.smsStores:
                if s[0] == store:
                    realStore = s[1]
                    break
            if not realStore:
                raise Exception('Invalid sms store: %s' % store)
        else:
            realStore = 'ALL'
        res = self.cmd('AT+CMGL=%s' % realStore, bufsize=50, raw=True)
        log.warn('todo: not finished: cmd_listSms() !')
        return res

    def cmd_getSmsUsage(self):
        ret = {}
        res = self.cmd('AT^SLMS', raw=True)
        for line in res:
            line = line.strip()
            if not line: continue
            tmp = line.split('SLMS:')
            if len(tmp) != 2:
                raise Exception('Unknown response: %s' % res)
            tmp = tmp[1].strip().split(',')
            tmp[0] = tmp[0][1:-1] # remove quotes
            if tmp[0] == 'MT':
                key = 'total'
            elif tmp[0] == 'SM':
                key = 'sim'
            elif tmp[0] == 'ME':
                key = 'memory'
            ret[key] = {'total': int(tmp[1]), 'used': int(tmp[2])}
        return ret

    def cmd_sendSms(self, number, message):
        log.info('sendSms: %s : %s' % (number, message))
        id = None
        res = self.cmd('at+cmgs="%s"' % number, raw=True)
        #log.info('sendSms result: %s' % res)
        if (type(res) in (type([]),type((1,))) and res[0] == '>') or res == '>':
            res = self.cmd('%s\x1A' % message, bufsize=5, raw=True)
            log.info('sendSms result2: %s' % res)
            if res and len(res) > 1:
                # id = res[1].split(":")[1].strip()
                id = res.split(":")[1].strip()
            else:
                log.warn("Unknown result2: %s" % res)
        else:
            log.warn("Unknown result1: %s" % res)
        return id

    def cmd_getSms(self, id):
        return self.getSms(id)

    def cmd_deleteSms(self, id):
        return self.deleteSms(id)

    def cmd_sendPin(self, pin):
        return self.trySendPin(force=True, pin=pin)

    def cmd_sendConfigPin(self):
        return self.trySendPin(force=True)

    def cmd_getPinStatus(self):
        return self.cmd('at+cpin?')

    def cmd_getInfo(self):
        data = {}
        map = {
            'gcap': 'gsm.capabilities',
            'cgmi': 'brand',
            'cgmm': 'model',
            'cgmr': 'revision',
            'cgsn': 'serial',
            'cimi': 'gsm.subscription.id',
        }
        # capabilities, manufacturer, model, revision, serial, international subscr id
        for k in ['gcap','cgmi','cgmm','cgmr','cgsn','cimi']:
            data[map[k]] = self.cmd("at+%s" % k)
        return data

    def cmd_getClock(self, getTimestamp=False):
        res = self.cmd("at+cclk?")
        t = time.strptime(res, self.timeFormat)
        if getTimestamp:
            return time.mktime(t)
        else:
            return time.strftime('%Y-%m-%d %H:%M:%S', t)

    def cmd_setClock(self, dt):
        res = self.cmd('at+cclk="%s"' % time.strftime(self.timeFormat, dt))
        log.debug("setClock result: %s" % res)

    def cmd_getIndicators(self):
        data = {}
        keys = ['battchg', 'signal', 'service', 'sounder', 'message', 'call', 'roam', 'smsfull', 'rssi']
        res = self.cmd('at+cind?').split(',')
        for i in range(len(res)):
            data[ keys[i] ] = res[i]
        return data

    def cmd_getOperator(self):
        # mode,format,oper
        res = self.cmd('at+cops?').split(',')
        if len(res) < 3:
            return None
        return res[2].strip('"')

    def cmd_getSmsServiceNumber(self):
        res = self.cmd('at+csca?').split(',')
        return res[0].strip('"')

    def cmd_getSimcardId(self):
        return self.cmd('at+scid?')

    def cmd_getTemperature(self):
        res = self.cmd('at^sctm?', raw=True) #.split(',')
        try: res = res[0].split(':')[1].split(',')
        except IndexError: return None
        return res[2]


    def onDescribe(self):
        stores = []
        for item in self.smsStores:
            stores.append(item[0])
        return {
            'info': 'GSM Modem - Siemens MC35i Terminal (and others?)',
            'commands': [
                ('sendSms', [('number','str'),('message','str')]),
                ('getSms', [('id','int')]),
                ('listSms', [('store','str',stores, '(Optional, default=all)')], 'Not finished!'),
                ('getSmsUsage', []),
                ('deleteSms', [('id','int')]),
                ('getInfo', []),
                ('getClock', []),
                ('setClock', [('time','str')]),
                ('getIndicators', []),
                ('getOperator', []),
                ('getSmsServiceNumber', []),
                ('getSimcardId',[]),
                ('getTemperature',[]),
                ('sendPin',[('pin','int',None,'Pin code')]),
                ('sendConfigPin',[]),
                ('raw', [('command','str')], 'Send a raw command')
            ],
            'events': [
                ('smsReceived', ('key','str',['smsReceived']), ('value','str',None,'Message text'), ('extra','dict',{'callerid':'str','time':'str'}) ),
            ],
        }


class GsmModem2():

    def parseResult(self, data, cmd):
        # f.ex. an incoming sms may occur when we parse result of a command,
        # so do incoming check here also
        log.debug('Parseresult')
        log.debug('Parseresult data: %s' % data)
        log.debug('Parseresult cmd: %s' % cmd)
        for l in data:
            self.onIncoming(l, True)
        if len(data) == 1 or (len(data) == 3 and data[1] == '' and data[2] == 'OK'):
            res = self.parseResultLine(data[0], cmd)
            if res:
                return res
            else:
                return data[0]
        elif len(data) == 4 and data[0] == '' and data[2] == '' and data[3] == 'OK':
            return data[1]
        else:
            log.warn("Unknown result: %s" % data)
            return data

    def parseResultLine(self, data, cmd):
        #log.info("line: %s" % data)
        pat = re.compile('\+([A-Z]+): (.+)')
        m = pat.match(data)
        if not m: 
            return None
        pre = m.group(1)
        val = m.group(2)
        val = val.strip().strip('"')
        return val



if __name__ == '__main__':
    log.level = 'debug'
    o = GsmModemService()
    conf = {'main': { 'serial.service': '/dev/ttyS1' }}
    o.config = conf
    o.setup(conf=conf)
    o.cmd_sendPin(pin=4606)
    #time.sleep(5)
    #o.open()
    t = Thread(target=o.open)
    t.setDaemon(True)
    t.start()
    #o.getSms(157)
    for i in range(8):
        print i
        if i == 4:
            o.onCommand('sendSms',['+4791000000','hallo'])
        time.sleep(0.5)

