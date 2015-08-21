import rrdtool, time, os
from chains.common import log

class Plot:

    def __init__(self, id, path, label, source, interval):
        self.id         = id
        self.path       = path
        self.source     = source
        self.interval   = interval
        self.lastUpdate = None
        self.label      = label

    def isDue(self):
        if not self.lastUpdate:
            return True
        if (time.time() - self.lastUpdate) > self.interval:
            return True
        else:
            return False

    def plot(self, value, timestamp):
        self.create()
        self.lastUpdate = timestamp
        value           = self.sanitizeValue(value)
        args = [self.path.encode('utf-8'), '%s:%s' % (timestamp, value)]
        rrdtool.update(*args)

    def create(self):
        if os.path.exists(self.path):
            return
        # todo: DS and RRA params should be configurable
        args = [
            self.path.encode('utf-8'),

            '-b %s' % (int(time.time()-(60*60))), # start - TMP!
            '-s %s' % self.interval, # step
            
            # RRA:cf:xff:steps:rows
            'RRA:AVERAGE:0.5:1:10080',   # one week of 1min
            'RRA:AVERAGE:0.5:5:17280',   # two months of 5min
            'RRA:AVERAGE:0.5:30:17520',  # one year of 30min
            'RRA:AVERAGE:0.5:120:43800', # 10 years of 2hrs

            # DS:name,type,heartbeat,min,max
            # other types = gauge,counter,derive,absolute,compute
            # configurable in last chains version = type, heartbeat, min, max
            'DS:data:GAUGE:%s:0:10000000' % (self.interval*2),
        ]
        rrdtool.create(*args)

    def delete(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def sanitizeValue(self, value):
        if not value:
            return 0
        if value == True:
            return 1
        return value

if __name__ == '__main__':

    id       = 'foo'
    filename = '/tmp/foo.rrd'
    source   = 'test.value'
    interval = 60
    label    = 'Foo'

    plot = Plot(id, filename, label, source, interval)

    plot.delete()
    if os.path.exists(filename):
        raise Exception("file exists after delete: %s" % filename)

    plot.create()
    if not os.path.exists(filename):
        raise Exception("file does not exist after create: %s" % filename)

    step  = 0
    count = 30
    start = time.time() - (count*interval)
    now   = start
    while step < count:
        print "plot %s @ %s" % (step,now)
        step += 1
        plot.plot(step, now)
        now += interval

    print ""
    print "data written to: %s" % filename
    print "to check if it has data: rrdtool fetch /tmp/foo.rrd AVERAGE"
    print ""
    print "tests successfull :)"
    print ""
