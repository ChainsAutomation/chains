import rrdtool, time, os
from chains.common import log

class GraphSimple:

    def __init__(self, id, plots, path, width, height, stack=False):
        self.id        = id
        self.plots     = plots
        self.path      = path
        self.stack     = stack
        self.colors = [
            ('008800','ddffdd'), ('880000','ffdddd'), ('000088','ddddff'),
            ('008888','ddffff'), ('888800','ffffdd'), ('880088','ffddff')
        ]
        self.colorIndex = -1
        self.width  = width
        self.height = height

    def graph(self, start, end):

        consolidationFunction = 'AVERAGE'

        data = [
            self.path.encode('utf-8')
        ]

        index = 0
        for plot in self.plots:

            index += 1
            color = self.getColor(index)
            stack = ''
            if self.stack: stack = 'STACK'

            data.append(
                # DEF:key=file:datasource:cf
                'DEF:data%s=%s:data:%s' % (index, plot.path, consolidationFunction)
            )
            data.append(
                # AREA:key#color:label:STACK
                'AREA:data%s#%s:%s:%s' % (index, color[1], '', stack)
            )

        index = 0
        for plot in self.plots:

            index += 1
            color = self.getColor(index)
            stack = ''
            if self.stack and index > 1: stack = 'STACK'
            label = plot.label
            data.append(
                # LINE:key#color:label:STACK
                'LINE1:data%s#%s:%s:%s' % (index, color[0], label, stack)
            )

        data.append('-w %s' % self.width)
        data.append('-h %s' % self.height)
        if start: data.append('-s %s' % int(start))
        if end:  data.append('-e %s' % int(end))

        args = []
        for arg in data:
            if type(arg) == type(u''):
                arg = arg.encode('utf-8')
            args.append(arg)

	#print('data: %s'%(args,))
        log.info('graph.args: %s' % (args,))

        rrdtool.graph(*args)

    def getColor(self, index):
        if index >= len(self.colors):
            index = 0
        return self.colors[index]

if __name__ == '__main__':

    import Plot

    plot    = Plot.Plot('foo', '/tmp/foo.rrd', 'Foo', None, 60)
    imgfile = '/tmp/foo.png'
    start   = time.time() - (60*30)
    end     = None  # ie. now

    if not os.path.exists(plot.path):
        raise Exception("rrdfile does not exist: %s\nrun Plot.py test first?" % plot.path)

    g = GraphSimple('foo', [plot], imgfile, 300, 150)
    g.graph(start, end)

    if not os.path.exists(imgfile):
        raise Exception("imgfile does not exist after graphing: %s" % imgfile)

    print ""
    print "graph written to: %s" % imgfile
    print "all tests successfull :)"
    print ""
