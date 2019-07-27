from __future__ import absolute_import
import chains.service
from chains.common import log
from . import adapter

class EspruinoService(chains.service.Service):

    def onInit(self):

        # todo: support multiple addresses/devices

        log.info('EspruinoService.onInit: device=%s' % self.config.get('address'))

        c = adapter.Config()
        c.addDevice(adapter.ConfigDevice(
            address = self.config.get('address'),
            advertismentKeys=['button.buttonCount','button.buttonLength', 'battery.battery','temperature.temperature','light.light'],
            jsProgram = adapter.ProgramFileReader('program.js').read(),
            callback = self.btEventCallback
        ))
        self.adapter = adapter.Adapter(c, log)


    def onStart(self):
        self.adapter.run()

    def onShutdown(self):
        self.adapter.stop()

    def action_reset(self):
        self.adapter.sendProgram('reset();')

    """ todo: add startBlinkRed, stopBlinkRed, etc.. to js-program
    def action_blink(self, index, toggle):
        index = int(index)
        if index != 1 and index != 2:
            raise Exception('Only index 1 and 2 supported')
        toggleString = 'false'
        if toggle:
            toggleString = 'true'
        self.queueProgram('setBlink(%s, %s);' % (index, toggleString))
    """

    # tuba todo
    def btEventCallback(self, address, key, values):
        log.info('btEventCallback: %s = %s' % (key, values))

        device = key
        deviceAttributes = {}

        # todo: lookup device name from address
        #deviceAttributes['device'] = device
        deviceAttributes['device'] = device # now battery, temperature, etc

        data = {}
        for valueKey in values:
            valueValue = values[valueKey]
            data[valueKey] = {"value": valueValue}
        log.info('sendEvent: data=%s attr=%s' % (data, deviceAttributes))

        self.sendEvent('change', data, deviceAttributes)

