#!/usr/bin/python
import vobject
import sys
import datetime
import time
from dateutil.parser import *

from chains.service import Service
from chains import utils
##from chains.log import Log

# cal.contents['vevent'][3].contents['dtstamp'][0].value
# cal.contents['vevent'][3].contents['valarm'][0].contents['description'][0].value()
# if ( cal.contents['vevent'][3].__class__ == vobject.icalendar.RecurringComponent ):
#for ev in cal.vevent_list:
# print cal.contents['vevent'][3].contents['uid'][0]
# <UID{}8>
# print cal.contents['vevent'][3].contents['uid'][0].value
# 8
# type(cal.contents['vevent'][3].contents['uid'][0])
# <class 'vobject.base.ContentLine'>

class IcalHaService(Service):

    def init(self):
        self.reader = IcalHaReader(self)
        #self.reader.setDaemon(True)
        pass

    def open(self):
        self.reader.run()

    def close(self):
        self.reader.stop = True

    def onEvent(self, alarmlabel, cal, data):
        if(data.__class__ == unicode or data.__class__ == str):
            extradata = {'message': data}
        elif(data.__class__ == dict):
            extradata = data
        else:
            print 'unknown, skipping'
        evt = {
            'service': self.config['id'],
            'key': cal, # /dev/sda
            'value': alarmlabel, # 44
            'extra': extradata
        }
        self.devDaemon.onEvent(evt)

    def onCommand(self, command, args):
        if command == 'timer':
            if len(args) != 3:
                raise Exception("Need 3 args")
            # minutes, label, msg
            now = datetime.datetime.now()
            alertmins = int(args[0])
            adelta = datetime.timedelta(minutes=alertmins)
            atime = now + adelta
            self.reader.tempalarms.append([atime,args[1],args[2]])
        elif command == 'addvtodo':
            if len(args) != 1:
                raise Exception("Need 1 arg")
            self.reader.addvtodo(args[0])
        elif command == 'addvevent':
            if len(args) > 0:
                raise Exception("Need 0 args")
            self.reader.addvevent()
        else:
            Log.info("No such command: %s" % command)
            return False
        # setCustomCharacter
        return True


    def onDescribe(self):
        return {
            'info': 'iCalendar service',
            'commands': [
                ('timer', [('minutes', 'int'),('label','str'),('message','str')], 'Creates a timer event from service'),
                ('addvtodo', [('number', 'str')], 'Add todo -NOT WORKING-'),
                ('addvevent', [], 'Add event -NOT WORKING-'),
            ],
            'events': [
                ('timer', ('label','str',[]),('message','str',[]) )
            ],
            'serial': '1337'
        }


# TODO: timezones?
class IcalHaReader():

    def __init__(self, service):
        self.stop = False
        self.reload = False
        self.service = service
        self.checkinterval = 5.0
        self.depth = 0
        self.debug = 0
        # alarms = [datetime, calLabel, type, uid, alarmlabel]
        self.caldict = {}
        self.alarms = []
        self.tempalarms = []
        # move to config, add support for http+auth
        self.calendars = {}
        self.defalarms = {}

        self.getconfig()
        self.reloadcals()

    def getconfig(self):
        print "getconfig()"
        try:
            checkinterval = self.service.config['main']['checkinterval'] 
        except KeyError:
            print 'checkinterval not in config, using defaults'

        for key in self.service.config:
            # all sections that are not main are calendars
            caldict = {}
            # if key != 'main' and key != 'id':
            if key != 'main' and key != 'id' and key != 'extra' and key != 'logoptions' and key != 'logfiles':
                print key
                try:
                    print self.service.config[key]
                    file = self.service.config[key]['file']
                    caldict.update({'file': file})
                    #print 'serial: ' + serial
                except KeyError:
                    print "file must be specified in config"
                    sys.exit(1)
                try:
                    defalarms = self.service.config[key]['defaultalarms']
                    daparts = defalarms.split(',')
                    partdict = {}
                    for part in daparts:
                        pkey,pval = part.split(':')
                        partdict.update({ pkey: pval })
                    self.defalarms.update({key: partdict})
                except KeyError:
                    print "no defaultalarms defined"
                try:
                    user = self.service.config[key]['username']
                    caldict.update({'username': user})
                except KeyError:
                    self.dprint("no username defined")
                try:
                    passwd = self.service.config[key]['password']
                    caldict.update({'password': passwd})
                except KeyError:
                    self.dprint("no password defined")
                #dprint('defalarms: ')
                #print self.defalarms
                #print 'caldict: ',
                #print caldict
                self.calendars.update({key:caldict})
                #print 'Calendar Ends.'
        #print 'Calendars:'
        #print self.calendars


    def run(self):
        while not self.stop:
            self.reader()

    def reader(self):
        print "reading",
        # TODO: Move reload to commands?
        if(self.reload):
            self.reloadcals()
        now = datetime.datetime.now()
        print now
        item = 0
        # iCal alarms
        while (item < (len(self.alarms))):
            # print self.alarms
            # print self.alarms[item][0]
            if(self.alarms[item][0] < now):
                # TODO: send event, remove from cal?, remove alarm
                print "alarm in the past, send event"
                rcal = self.alarms[item][1]
                rtype = self.alarms[item][2]
                ruid = self.alarms[item][3]
                try:
                    summary = self.caldict[rcal][rtype][ruid]['SUMMARY']
                except KeyError:
                    summary = 'iCalEvent'
                # the alarm item in the calendar:
                #print self.caldict[rcal][rtype][ruid]
                self.service.onEvent(rcal, self.caldict[rcal][rtype][ruid]['SUMMARY'], self.caldict[rcal][rtype][ruid])
                self.alarms.pop(item)
            item = item + 1
            print 'item: ',
            print item
            #else:
                #self.dprint("alarm still in the future:")
                #print self.alarms[item]
                #[datetime.datetime(2009, 5, 21, 7, 59, 59, 999852), 'test', u'vevent', u'28e3e21f-485c-4fb1-bfd9-dd5aea35a500', 'oneday']
        # timer alarms
        print 'tempalarms:'
        print self.tempalarms
        item = 0
        while (item < (len(self.tempalarms))):
            if(self.tempalarms[item][0] < now):
                # TODO: send event, remove alarm
                print "alarm in the past, send event"
                self.service.onEvent(self.tempalarms[item][1], 'timer', self.tempalarms[item][2])
                self.tempalarms.pop(item)
            else:
                print "alarm still in the future:"
                print self.tempalarms[item]
                #rcal = self.tempalarms[item][1]
                #rtype = self.tempalarms[item][2]
                #ruid = self.tempalarms[item][3]
            item = item + 1
        time.sleep(self.checkinterval)

    def dprint(self, string):
        if (self.debug == 1):
            print '\t' * self.depth + string

    def reloadcals(self):
        print "reloadcals()..."
        self.reload = False
        for key in self.calendars:
            print key
            passalarms = {}
            for label in self.defalarms[key]:
                alertmins = int(self.defalarms[key][label])
                adelta = datetime.timedelta(minutes=alertmins)
                passalarms.update( {label:adelta} )
            #print passalarms
            if(self.calendars[key]['file'][0] == '/'):
                f = file(self.calendars[key]['file'])
            elif(self.calendars[key]['file'][0:4] == 'http'):
                if self.calendars[key].has_key('user') and self.calendars[key].has_key('passwd'):
                    f = utils.fetchurl(
                        self.calendars[key]['file'],
                        self.calendars[key]['user'],
                        self.calendars[key]['passwd'],
                        gethandle=True
                    )
                else:
                    f = utils.fetchurl(self.calendars[key]['file'], gethandle=True)
                    print dir(f)
            else:
                raise Exception('Unhandled file/uri: %s' % self.calendars[key]['file'])
            cal = vobject.readOne(f)
            res = self.attribval(cal) 
            newalarms,newcal = self.getalarms(res,passalarms)
            # print newcal
            # {VCALENDAR : {}}
            for calkey in newcal:
                print calkey
                self.caldict.update({ key: newcal[calkey]})
            #self.caldict.update(newcal)
            for aitem in newalarms:
                aitem.insert(1,key)
                self.alarms.append(aitem)
            # self.alarms.append(newalarms)
        # print self.alarms
        #print self.caldict

    def timediff(self, dateobj):
        #print 'timediff()... '
        #print 'When: ',
        #print dateobj
        now=datetime.datetime.now()
        #print 'Now:',
        #print now
        if(dateobj.__class__ == datetime.datetime):
            #print 'datetime.datetime'
            # remove tzinfo, make naive, we expect same time zone.
            tdiff = dateobj.replace(tzinfo=None) - now
            if(tdiff.days < 0):
                return False
            return tdiff
        elif(dateobj.__class__ == datetime.date):
            #print 'datetime.date'
            # If event is an all day event, the event starts at 8:00 :)
            t = datetime.time(8, 0, 0)
            fulldate = datetime.datetime.combine(dateobj, t)
            # remove tzinfo, make naive, we expect same time zone.
            tdiff = fulldate.replace(tzinfo=None) - now
            if(tdiff.days < 0):
                return False
            return tdiff
        elif(dateobj.__class__ == unicode):
            #print "unicode string: ",
            #print dateobj
            today = datetime.date.today()
            t = datetime.time(8, 0, 0)
            defaultdate = datetime.datetime.combine(today, t)
            try:
                # dateutil.parse
                parseddate = parse(dateobj, ignoretz=True, default=defaultdate)
            except ValueError:
                #print "parse failed"
                return False
            print parseddate

        else:
            print "unknown date format: ",
            print type(dateobj)
            print dateobj.__class__
            return False


    def rrulenext(self,startdate,rrules):
        # TODO: Check for 'UNTIL', return False if in the past.
        rruledict = {}
        now = datetime.datetime.now()
        for rrule in rrules:
            (key, value) = rrule.split('=')
            rruledict.update( {key: value} )
        try:
            # False if UNTIL is in the past.
            if(not self.timediff(rruledict['UNTIL'])):
                return False
        except KeyError:
            pass

        # TODO: YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY
        if(rruledict['FREQ'] == 'YEARLY'):
            print "yearly frequency"
            multip = 1
            startyear = startdate.year
            newdate = startdate
            while not(self.timediff(newdate)):
                newyear = startyear + (int(rruledict['INTERVAL']) * multip)
                newdate = startdate.replace(year=newyear)
                print newdate
                multip = multip + 1
            return newdate
        elif(rruledict['FREQ'] == 'MONTHLY'):
            print "monthly frequency"
            multip = 1
            startyear = startdate.year
            startmonth = startdate.month
            newdate = startdate
            while not(self.timediff(newdate)):
                newmonth = startmonth + (int(rruledict['INTERVAL']) * multip)
                if(newmonth > 12):
                    extrayears = newmonth/12
                    modmonth = newmonth%12
                    newyear = startyear + extrayears
                    newdate = startdate.replace(year=newyear,month=modmonth)
                else:
                    multip = multip + 1
            return newdate
        elif(rruledict['FREQ'] == 'WEEKLY'):
            print "weekly frequency"
            multip = 1
            weekdelta = datetime.timedelta(days=7)
            newdate = startdate
            while not(self.timediff(newdate)):
                newdate = weekdelta * multip
                multip = multip + 1
                print newdate
            return newdate
        elif(rruledict['FREQ'] == 'DAILY'):
            # datetime.timedelta(days=1)
            print "daily frequency"
            multip = 1
            daydelta = datetime.timedelta(days=1)
            newdate = startdate
            while not(self.timediff(newdate)):
                newdate = daydelta * multip
                multip = multip + 1
                print newdate
            return newdate

    # Returns an associative array when given a vobject (ical) object
    # Uses recursion
    def attribval(self, attrib):
        self.depth += 1
        result = {}
        items = []
        count = 0
        if(attrib.__class__ != list):
            items.append(attrib)
        else:
            items = attrib
        for item in items:
            if( item.__class__ == vobject.base.Component ):
                self.dprint('Got vobject.base.Component')
                result = {}
                subres = {}
                for key in item.contents:
                    self.dprint("key: " + str(key))
                    val = self.attribval(item.contents[key])
                    subres.update( {key: val} )
                result.update( { item.name: subres } )
            elif( item.__class__ == vobject.base.ContentLine ):
                self.dprint('Got vobject.base.ContentLine')
                result = {}
                result.update( {item.name: item.value })
            elif( item.__class__ == vobject.icalendar.TimezoneComponent):
                self.dprint('Got vobject.icalendar.TimezoneComponent')
                result = {}
                result.update( {'time': 'datime'} )
            elif( item.__class__ == vobject.icalendar.RecurringComponent ):
                self.dprint('Got vobject.icalendar.RecurringComponent')
                if(item.contents.has_key('uid')):
                    uiddict = self.attribval(item.contents['uid'])
                    uid = uiddict.values()[0]
                    subres = {}
                    for key in item.contents:
                        res = self.attribval(item.contents[key])
                        subres.update( res )
                    result.update( {uid: subres} )
            else:
                print '\t\tGot UNKNOWN: ',
                print type(item)
                result.append(item)
        self.depth -= 1
        count += 1
        # print 'Dir: ',
        # print dir(result)
        # print result
        if(type(result) == dict):
            return result
        else:
            return result


    def getalarms(self,cal,almdeltas):
        # TODO: remove cal entries in the past.
        alarmarray = []
        # res = self.attribval(cal) 
        # print "-- ############################## --"
        now = datetime.datetime.now()
        for calendar in cal:
            #print "Calendar:"
            #print calendar
            for type in cal[calendar]:
                #print "type:"
                #print type
                if(type == 'vevent'):
                    #print "vevents"
                    # print res[calendar][type]
                    for uid in cal[calendar][type]:
                        #print 'uid: ' + str(uid)
                        # print res[calendar][type][uid]
                        # check for recurrence rule
                        try:
                            rrule = cal[calendar][type][uid]['RRULE']
                        except KeyError:
                            rrule = False
                        # Find how long into the future the event begins
                        tdiff = self.timediff(cal[calendar][type][uid]['DTSTART'])
                        # If event is in the future
                        if(tdiff):
                            #print "Date in the future: ",
                            #print "Adding alarm(s)"
                            #print tdiff
                            for alarm in almdeltas:
                                newalarm = now + tdiff - almdeltas[alarm]
                                alarmarray.append([newalarm, type, uid, alarm])
                        # If event has rrule
                        elif(rrule):
                            #print 'in past but has rrule:'
                            rrules = cal[calendar][type][uid]['RRULE'].split(';')
                            nextdate = self.rrulenext(cal[calendar][type][uid]['DTSTART'],rrules)
                            if(nextdate):
                                tdiff = self.timediff(nextdate)
                                #print nextdate
                                #print tdiff
                                for alarm in almdeltas:
                                    #print alarm
                                    #print almdeltas[alarm]
                                    newalarm = now + tdiff - almdeltas[alarm]
                                    #print newalarm
                                    alarmarray.append([newalarm, type, uid, alarm])
                            #else:
                            #    print "rrule is in the past"
                        #else:
                        #    print 'Date in the past, skipping...'
                elif(type == 'vtodo'):
                    print 'vtodos'
                else:
                    print 'skipping...'
        # alarmarray = [datetime.datetime.now(), 'calName', 'event', 'uid', 'alabel']
        return alarmarray, cal


#reader = IcalHaReader()
#reader.run()
#reader.reader()

if __name__ == "__main__":
    d = IcalHaService()
    d.init()
    d.open() 
