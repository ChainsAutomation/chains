from chains.service import Service
from chains.common import log, config
import util
#import os, copy, datetime, time, logging, logging.handlers

# https://github.com/PiSupply/PaPiRus

class PapirusService(Service):

    def onInit(self):
        self.rotation = self.config.getInt('rotation')
        if not self.rotation:
            self.rotation = 0
        if self.rotation not in [0,90,180,270]:
            log.warn("Invalid config main.rotation: %s, valid is: 0 or 90 or 180 or 270, will use 0")
            self.rotation = 0
        log.info('startup. rotation=%s' % self.rotation)

    def action_textFill(self, text):
        """
        Display text that fills screen
        @param   text   string   Text to display
        """
        util.writeFullWidth(text)

    def action_textCenter(self, text, size=20):
        util.writeCenter(text, size)

    def ation_textPosition(self, text, x=0, y=0, size=20):
        display = PapirusTextPos()
        display.AddText(text, x, y, size)
        display.Writeall()
