import chains.device
from chains.common import log
import time, datetime
import RPi.GPIO as GPIO
import picamera

class RPiDevice(chains.device.Device):

    def onInit(self):
        self.interval = self.config.get('interval'):
        if not self.interval:
            self.interval = 60
        self.model_version = self.config.get('model_version')
        if not self.model_version:
            self.model_version = 2
        self.model_type = self.config.get('model_type')
        if not self.model_type:
            self.model_version = 'b'

    def onStart(self):
        last = {}
        while not self._shutdown:
            t = datetime.datetime.now()
            time.sleep(self.interval)

    def action_camled(self, action):
        '''
        Change the led on rpi camera
        @param  action  string  Set the camera led on or off
        '''
        if self.model_version > 1 or self.model_type.upper == 'B+':
            led_gpio = 32
        else:
            led_gpio = 5
        GPIO.setup(led_gpio, GPIO.OUT, initial=False)
        if action == 'on':
            GPIO.output(led_gpio, True)
            return {'cam_led':'on'}
        elif action == 'off':
            GPIO.output(led_gpio, False)
            return {'cam_led':'off'}
        else:
            return False

# /opt/vc/bin/raspistill
