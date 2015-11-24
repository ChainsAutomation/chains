import chains.service, time, random
from chains.common import log

class TestService(chains.service.Service):

    def onInit(self):
        while True:
            self.sendEvent(
                'volume',
                { 'volume': { 'value': round(random.random()*100), 'actions': ['volumeUp','volumeDown'] } },
                { 'device': 'onkyo', 'type': 'amplifier' }
            )
            time.sleep(1)
            self.sendEvent(
                'brightness',
                { 'brightness': { 'value': 100, 'actions': ['dim'] } },
                { 'device': 'lamp-1', 'type': 'lamp' }
            )
            time.sleep(0.5)
            self.sendEvent(
                'state',
                { 'state': { 'value': 'on', 'actions': ['on','off'] } },
                { 'device': 'lamp-1', 'type': 'lamp' }
            )
            time.sleep(0.5)
            self.sendEvent(
                'change',
                {
                    'state': { 'value': 'off', 'actions': ['on','off'] },
                    'brightness': { 'value': 0, 'actions': ['dim'] }
                },
                { 'device': 'lamp-1', 'type': 'lamp' }
            )
            time.sleep(random.random()*10)
