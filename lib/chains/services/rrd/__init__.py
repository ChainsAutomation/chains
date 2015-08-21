import chains.service
from chains.common import log, amqp
import rrdtool, time, os

from Config import Config

class RrdService(chains.service.Service):

    def onInit(self):
        self.dataPath     = self.config.getDataDir()
        config            = Config(self.config.data(), self.dataPath)
        self.plots        = config.getPlots()
        self.graphs       = config.getGraphs()
        self.interval     = self.determineInterval()
        log.info('Service started with %s plots, %s graphs, interval %s' % (len(self.plots), len(self.graphs), self.interval))

    def onStart(self):
        while not self._shutdown:
            now = time.time()
            for plot in self.plots:
                if plot.isDue():
                    value = self.getPlotValue(plot)
                    log.info('Plot %s = %s @ %s' % (plot.id, value, now))
                    plot.plot(value, now)
                else:
                    log.debug('Plot %s is not due yet @ %s' % (plot.id, now))
            time.sleep(self.interval)

    def action_graph(self, id, start=None, end=None):
        graph = self.getGraph(id)
        if not graph:
            raise Exception('No such graph: %s' % id)
        log.info('graph: %s %s => %s' % (id,start,end))
        graph.graph(start, end)
        return graph.path

    def getGraph(self, id):
        for graph in self.graphs:
            if graph.id == id:
                return graph

    def getPlotValue(self, plot):

        reactorId = self.config.get('reactor') #'skallemann' # todo: config, with sensible default (ie. same host or get auto if one)

        source    = plot.source.split('.')
        service    = source.pop(0)
        key       = source.pop(0)
        stateKey  = '%s.%s.data.%s' % (service, key, '.'.join(source))

        log.debug("getPlotValue.RPC request: ra.%s.getState( %s )" % (reactorId, stateKey))

        conn      = amqp.Connection()
        rpc       = conn.rpc()

        result = rpc.call('ra.%s.getState' % reactorId, [stateKey])
        log.debug("getPlotValue.RPC result: %s" % (result,))

        if not result:
           return 0

        return float(result) 

    def determineInterval(self):
        interval = None
        for plot in self.plots:
            if interval == None or plot.interval < interval:
                interval = plot.interval
        if interval == None:
            interval = 60
        return interval

