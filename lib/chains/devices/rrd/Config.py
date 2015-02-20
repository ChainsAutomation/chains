from Plot import Plot
from GraphSimple import GraphSimple
from GraphCustom import GraphCustom

import os

class Config:
    def __init__(self, configData, dataDir):
        self.width  = 300
        self.height = 150
        self.data   = configData
        self.dir    = dataDir
        self.makeDirs()

    def makeDirs(self):
        dirs = [self.dir + '/rrd', self.dir + '/graph']
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def getPlots(self):

        if not self.data.has_key('plots') or not self.data['plots']:
            return []

        data = {}
        for key in self.data['plots']:
            id,attr = key.split('.')
            if not data.has_key(id):
                data[id] = {}
            data[id][attr] = self.data['plots'][key]

        plots = []
        ids   = data.keys()
        ids.sort()
        for id in ids:

            item = data[id]

            item['id']   = id
            item['path'] = '%s/rrd/%s.rrd' % (self.dir, id)
            if not item.has_key('label') or not item['label']:
                item['label'] = id
            if not item.has_key('interval') or not item['interval']:
                item['interval'] = 60
            item['interval'] = int(item['interval'])

            if not item.has_key('source') or not item['source']:
                raise Exception('Plot %s has no source value' % id)
            tmp = item['source'].split('.')
            if len(tmp) < 3:
                raise Exception("Plot %s - source value should be least 3 items separated by dot, f.ex: mydev.mykey.value, timer.minute.value, bluetooth.arrivedguest.count, etc...")

            plots.append(Plot(**item))

        return plots

    def getPlot(self, id):
        for plot in self.getPlots():
            if plot.id == id:
                return plot

    def getGraphs(self):

        if not self.data.has_key('graphs') or not self.data['graphs']:
            return []

        data = {}
        for key in self.data['graphs']:
            id,attr = key.split('.')
            if not data.has_key(id):
                data[id] = {}
            data[id][attr] = self.data['graphs'][key]

        graphs = []
        ids   = data.keys()
        ids.sort()
        for id in ids:

            item = data[id]

            if not item.has_key('plots'):
                raise Exception('Graph %s has no plot value' % id)

            item['id']    = id
            item['path']  = self.dir + '/graph/' + id + '.png'

            plots = []
            for key in item['plots'].split(','):
                plot = self.getPlot(key.strip())
                if not plot:
                    raise Exception('Graph %s - no such plot: %s' % (id, key))
                plots.append(plot)
            item['plots'] = plots

            if not item.has_key('width') or not item['width']:
                item['width'] = self.width
            if not item.has_key('height') or not item['height']:
                item['height'] = self.height

            if data[id].has_key('definition') and data[id]['definition']:
                graphs.append(GraphCustom(**data[id]))
            else:
                graphs.append(GraphSimple(**data[id]))

        return graphs


if __name__ == '__main__':

    def _assert(v1,v2):
        if v1 != v2:
            raise Exception("Mismatch: %s != %s" % (v1,v2))

    c = Config(
        {
            'plots': {
                'p2.label':    'My other data',
                'p1.source':   'mydev.mykey.value',
                'p2.source':   'mydev2.mykey2.value2',
                'p2.interval': 30
            },
            'graphs': {
                'g1.plots':      'p1',
                'g2.plots':      'p1,p2',
                'g2.definition': 'DEF:data1=$p1:data:AVERAGE LINE:temp1#ff0000:Kake:',
                'g2.width':      1000,
                'g2.height':     800,
            }
        },
        '/tmp'
    )
    plots = c.getPlots()

    _assert(plots[0].label,     'p1')
    _assert(plots[0].source,    'mydev.mykey.value')
    _assert(plots[0].interval,  60)
    _assert(plots[0].id,        'p1')
    _assert(plots[0].path,      '/tmp/rrd/p1.rrd')

    _assert(plots[1].label,     'My other data')
    _assert(plots[1].source,    'mydev2.mykey2.value2')
    _assert(plots[1].interval,  30)
    _assert(plots[1].id,        'p2')
    _assert(plots[1].path,      '/tmp/rrd/p2.rrd')

    graphs = c.getGraphs()

    _assert(graphs[0].plots[0].id, 'p1')
    _assert(graphs[0].width,       300)
    _assert(graphs[0].height,      150)
    _assert(graphs[1].plots[0].id, 'p1')
    _assert(graphs[1].plots[1].id, 'p2')
    _assert(graphs[1].definition,  'DEF:data1=$p1:data:AVERAGE LINE:temp1#ff0000:Kake:')
    _assert(graphs[1].width,       1000)
    _assert(graphs[1].height,       800)

    print 'all tests successfull :)'

