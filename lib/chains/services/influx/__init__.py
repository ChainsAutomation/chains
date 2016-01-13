from chains.service import Service
from chains.common import log

# from .system import System as SS

class InfluxService(Service):

    def onInit(self):
        pass

    def onStart(self):
        pass

    def onMessage(self, topic, data, correlationId):
        log.info("topic: " + str(topic))
        log.info("data: " + str(data))
    

    def getConsumeKeys(self):
        return ['#']


