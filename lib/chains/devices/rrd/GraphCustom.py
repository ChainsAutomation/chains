import rrdtool, time, os, re

class GraphCustom:

    def __init__(self, id, plots, definition, path, width, height):
        self.id         = id
        self.plots      = plots
        self.path       = path
        self.definition = definition
        self.width      = width
        self.height     = height

    def graph(self, start, end):

        data = [
            self.path.encode('utf-8')
        ]

        pattern = re.compile('.*(\$[^:]+).*')
        parts   = self.definition.split(' ')
        for part in parts:
            if part[0:3] == 'DEF':
                while True:
                    match = pattern.match(part)
                    if not match: break
                    key   = match.group(1)
                    value = self.findPlotPath(key[1:])
                    part = part.replace(key, value)
            data.append(part)

        data.append('-w %s' % self.width)
        data.append('-h %s' % self.height)
        if start: data.append('-s %s' % int(start))
        if end:  data.append('-e %s' % int(end))

        args = []
        for arg in data:
            if type(arg) == type(u''):
                arg = arg.encode('utf-8')
            args.append(arg)

        rrdtool.graph(*args)

    def getNextColor(self):
        self.colorIndex += 1
        if self.colorIndex >= len(self.colors):
            self.colorIndex = 0
        return self.colors[self.colorIndex]

    def findPlotPath(self, id):
        for plot in self.plots:
            if plot.id == id:
                return plot.path


if __name__ == '__main__':

    import Plot

    plot    = Plot.Plot('foo', '/tmp/foo.rrd', 'Foo', None, 60)
    imgfile = '/tmp/foo2.png'
    start   = time.time() - (60*30)
    end     = None  # ie. now

    if not os.path.exists(plot.path):
        raise Exception("rrdfile does not exist: %s\nrun Plot.py test first?" % rrdfile)

    g = GraphCustom(
        'foo2',
        [plot],
        'DEF:data1=$foo:data:AVERAGE LINE:data1#ff0000:Kake:',
        imgfile,
        300,
        150
    )
    g.graph(start, end)

    if not os.path.exists(imgfile):
        raise Exception("imgfile does not exist after graphing: %s" % imgfile)

    print ""
    print "graph written to: %s" % imgfile
    print "all tests successfull :)"
    print ""
