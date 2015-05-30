import chains.device
from chains.common import log
import time, datetime
import RPi.GPIO as GPIO
import picamera

class RPiDevice(chains.device.Device):

    def onInit(self):
        self.datadir = self.config.getDataDir()
        self.interval = self.config.getInt('interval') or 60
        self.model_version = self.config.getInt('model_version') or 2
        self.model_type = self.config.get('model_type') or 'b'

    # TODO: control gpio
    # def action_gpio(self, ... )

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

    def action_camcapture(self, imgname='image.jpg'):
        '''
        Capture an image using the rpi camera
        @param  imgname  string  Use the image filename
        '''
        camera = picamera.PiCamera()
        camera.capture(self.datadir + '/image.jpg')
        # sendevent picture captured with filename 

    def action_videorecord(self, vidname='video.h264', length=10):
        '''
        Record a video using the rpi camera
        @param  vidname  string  Use the video filename
        @param  length  int  Length of video in seconds
        '''
        camera.start_recording('video.h264')
        sleep(length)
        camera.stop_recording()
        # return instantly with a recording event and filename,
        # sendevent on video finished with filename

# /opt/vc/bin/raspistill
