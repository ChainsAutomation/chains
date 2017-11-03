from chains.service import Service
from chains.common import log, config
#import os, copy, datetime, time, logging, logging.handlers

# https://github.com/PiSupply/PaPiRus

class PapirusService(Service):

    def onInit(self):
        log.info('test')

    def action_text(self, text):
        """
        Set display text
        @param   text   string   Text to display
        """
        log.info("text: %s" % text)
