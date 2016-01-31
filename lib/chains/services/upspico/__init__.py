import chains.service
from chains.common import log
import time
import smbus

class UpsPicoService(chains.service.Service):

    def onStart(self):
        self.state = {}
        self.i2c = smbus.SMBus(1)
        interval = self.config.getInt('interval')
        while True:
            self.poll()
            time.sleep(interval)

    def poll(self):
        data = {
            'firmware': self.get_firmware_version(),
            'power_loss': self.get_power_loss(),
            'battery_voltage': self.get_battery_voltage(),
            'rpi_voltage': self.get_rpi_voltage(),
            'sot23_temperature': self.get_sot23_temperature(),
            'to92_temperature': self.get_to92_temperature(),
            'ad1': self.get_ad1(),
            'ad2': self.get_ad2(),
            'shutdown_time': self.get_shutdown_time(),
            'battery_temperature_on_error': self.get_battery_temperature_on_error()
        }

        for key in data.keys():
            value1 = data[key]
            value2 = self.state.get(key)
            if value2 == None or value1 != value2:
                self.state[key] = value1
                self.sendEvent(
                    key,
                    { key: { 'value': value1 }},
                    {}
                )

    def action_disable_buzzer(self):
        self.i2c.write_byte_data(0x6b, 0x0e, 0x00)

    def action_enable_buzzer_always(self):
        self.i2c.write_byte_data(0x6b, 0x0e, 0x01)

    def action_enable_buzzer_auto(self):
        self.i2c.write_byte_data(0x6b, 0x0e, 0x01)

    def get_power_loss(self):
        self.delay()
        data = self.i2c.read_byte_data(0x69, 0x00)
        data = data & ~(1 << 7)
        if (data == 1):
            return 0 # RPi
        elif (data == 2):
            return 1 # BAT
        else:
            return -1 # ERR

    def get_battery_voltage(self):
        self.delay()
        data = self.i2c.read_word_data(0x69, 0x01)
        data = format(data,"02x")
        return (float(data) / 100)

    def get_rpi_voltage(self):
        self.delay()
        data = self.i2c.read_word_data(0x69, 0x03)
        data = format(data,"02x")
        return (float(data) / 100)

    def get_firmware_version(self):
        self.delay()
        data = self.i2c.read_byte_data(0x6b, 0x00)
        data = format(data,"02x")
        return data

    def get_sot23_temperature(self):
        self.delay()
        data = self.i2c.read_byte_data(0x69, 0x0C)
        data = format(data,"02x")
        return data

    def get_to92_temperature(self):
        self.delay()
        data = self.i2c.read_byte_data(0x69, 0x0d)
        data = format(data,"02x")
        return data

    def get_ad1(self):
        self.delay()
        data = self.i2c.read_word_data(0x69, 0x05)
        data = format(data,"02x")
        return (float(data) / 100)

    def get_ad2(self):
        self.delay()
        data = self.i2c.read_word_data(0x69, 0x07)
        data = format(data,"02x")
        return (float(data) / 100)

    def get_shutdown_time(self):
        self.delay()
        data = self.i2c.read_word_data(0x6B, 0x09)
        data = format(data,"02x")
        return (float(data) / 100)

    def get_battery_temperature_on_error(self):
        self.delay()
        data = self.i2c.read_word_data(0x6B, 0x06)
        data = format(data,"02x")
        return (float(data) / 100)

    def delay(self):
        time.sleep(0.1)

