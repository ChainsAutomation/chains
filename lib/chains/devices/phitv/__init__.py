from chains.device import Device
from chains.common import log

import serial


class PhiTVDevice(Device):
    """Device implementing rs232 control on philips TVs and monitors"""

    def onInit(self):
        self.port = self.config.get('port') or "/dev/ttyUSB0"
        self.ser = serial.Serial(
            port=self.port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

    def onStart(self):
        log.info('Starting PhilipsTV')
        while not self._shutdown:
            data_raw = self.ser.readline()  # Using readline for now since this doesn't need performance
            data = self._parse_data(data_raw)
            self.sendEvent('phitv': data)

    def _parse_data(self, raw):
        # check data and return human readable data
        if raw:
            return {'msg': 'we have data'}
        else:
            return {'msg': 'no data'}

