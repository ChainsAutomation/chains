from chains.service import Service
from chains.common import log

# from .system import System as SS

class InfluxService(Service):

    def onInit(self):
        # interval between pushing aggregated stats
        self.interval = self.config.getInt(interval) or 60
        self.host = self.config.get('influxhost') or 'localhost'
        self.queryport = self.config.getInt('queryport') or 8086
        self.writemethod = self.config.get('writemethod') or 'http'
        if not self.config.getInt('writeport'):
            if self.writemethod == 'http':
                self.writeport = 8086
            elif self.writemethod == 'udp':
                self.writeport = 8089

    def onStart(self):
        pass

    def onMessage(self, topic, data, correlationId):
        log.info("topic: " + str(topic))
        log.info("data: " + str(data))

    def getConsumeKeys(self):
        return ['#']


