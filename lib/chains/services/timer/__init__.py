import chains.service
from chains.common import log
import time, datetime, re, copy

class TimerService(chains.service.Service):

    def onInit(self):
        self.sendSecond = False
        if self.config.getBool('sendsec'):
            self.sendSecond = True
        self.maxTimerId = 0
        self.timers = []
        self.interval = 1
        self.eventKeys = ['second', 'minute', 'hour', 'day', 'month', 'year']

    def onStart(self):
        last = {}
        while not self._shutdown:
            t = datetime.datetime.now()
            week = int(t.strftime("%W"))
            weekday = int(t.strftime("%w"))
            if weekday == 0:
                weekday = 7
            current = {
                'second': t.second,
                'minute': t.minute,
                'hour': t.hour,
                'day': t.day,
                'month': t.month,
                'year': t.year,
                'weekday': weekday,
                'week': week
            }
            for k in self.eventKeys:
                if not last.has_key(k) or current[k] != last[k]:
                    last[k] = current[k]
                    if k == 'second' and not self.sendSecond:
                        continue
                    evt = {'value': current[k]}
                    for k2 in current:
                        evt[k2] = current[k2]
                    self.sendEvent(k, evt)

            self.checkTimers(time.time())
            time.sleep(self.interval)

    def checkTimers(self, now):
        if not self.timers:
            return
        keep = []
        for timer in self.timers:
            if now >= timer['time']:
                self.doTimer(timer)
            else:
                keep.append(timer)
        self.timers = keep

    def doTimer(self, timer):
        self.sendEvent('timer-%s' % timer['key'], {
            'value': 'due',
            'label': timer['label']
            #'due': timestamp,
        })

    def parseTime(self, val):
        # Relative time
        val = '%s' % val
        patRelative = re.compile('(\d+)(d|h|m|s)?')
        m = patRelative.match(val)
        if m:
            val = float(m.group(1))
            ext = m.group(2)
            if ext:
                exts = {'s': 1, 'm': 60, 'h': (60*60), 'd': (60*60*24)}
                val = float(exts[ext])*val
            return time.time() + val
        # Absolute time
        patAbsolute = re.compile('(\d{4}-\d{2}-\d{2} )?(\d+:\d+)(:\d+)?')
        m = patAbsolute.match(val)
        if m:
            if not m.group(1):
                val = time.strftime('%Y-%m-%d') + ' ' + val
            if not m.group(3):
                val += ':00'
            t = time.strptime(val, '%Y-%m-%d %H:%M:%S')
            return time.mktime(t)
        # Invalid time
        raise Exception('Invalid time param: %s' % val)


    def action_addTimer(self, timestamp, key=None, label=None):
        if not key:
            self.maxTimerId += 1
            key = 'timer%s' % self.maxTimerId
        if not label:
            label = key
        timer = {'time': self.parseTime(timestamp), 'key': key, 'label': label}
        self.timers.append(timer)
        self.sendEvent('timer-%s' % key, {
            'value': 'running',
            'due': timestamp,
            'label': timer['label']
        })


    def action_getTimers(self):
        return self.timers

    def action_sleep(self, secs):
        time.sleep(float(secs))


    def onDescribe(self):

        # Generate events description for minute,hour,etc-events
        eventBase = {}
        for k in self.eventKeys:
            eventBase[k] = ('int', None, 'Current %s' % k)
        events = []
        for k in self.eventKeys:
            e = copy.copy(eventBase)
            e['key'] = ('str', [k], None)
            e['value'] = e[k]
            events.append((k, e, 'Sent every %s' % k))

        events.append((
            'timer-running', {
                'key': ('str', None, 'Custom alarm key, as set with addTimer action'),
                'value': ('str', ['running'], None),
                'due': ('int', None, 'Timestamp when alarm is done')
            }, 'Sent when a new timer is added'
        ))
        events.append((
            'timer-due', {
                'key': ('str', None, 'Custom alarm key, as set with addTimer action'),
                'value': ('str', ['due'], None)
            }, 'Sent when a new timer is due'
        ))

        return {
            'info': 'Sends time events every minute (or second), and does egg timers',
            'events': events
        }
 
