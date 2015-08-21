from chains.service import Service
from chains.common import log
import urllib2, urllib, sys, json

class PushoverService(Service):
    """Service implementing the push service on pushover.net"""

    def onInit(self):
        # Required parameters for pushover
        self.token = self.config.get('token')
        self.username = self.config.get('username')
        if not self.token or self.username:
            log.warn('Service needs token and username to work.')
            sys.exit(1)
        # Optional parameters for pushover
        #  TODO: optionally set default values for these in config
        self.pushurl = 'https://api.pushover.net/1/messages.json'

        self.message = self.config.get('message') or "Chains calling!"
        self.targetservice = self.config.get('targetservice')
        self.title = self.config.get('title')
        self.url = self.config.get('url')
        self.urltitle = self.config.get('urltitle')
        self.priority = self.config.getInt('priority') or 1  # "-2" no notification, -1 quiet notification, 1 - high priority, 2 requires confirmation by user
        self.sound = self.config.get('sound') or "bike" # https://pushover.net/api#sounds
        # self.timestamp, override servers timestamp, not needed as far as i can see

    def onStart(self):
        log.info('Starting PushoverService')
        #if not self.token or not self.username:
        #    log.warn('Service needs token and username to work.')
        #    return

    def action_push(self, message=None, targetservice=None, title=None, url=None, urltitle=None, priority=None, sound=None):
        '''
        Send a message using pushover.net
        @param  message     string   Text message you want to send
        @param  targetservice     string   Service to send to (optional)
        @param  title     string   Title of the message (optional)
        @param  url     string   URL to attach to the message (optional)
        @param  urltitle     string   Title of the URL (optional)
        @param  priority     int   Message priority: -2 no notification, -1 quiet notification, 1 - high priority, 2 requires confirmation by user (optional)
        @param  sound     string   Title of the message (optional)

        '''

        res = self._send_push(message, targetservice, title, url, urltitle, priority, sound)
        if res:
            return True
        else:
            return False

    def _send_push(self, message, targetservice, title, url, urltitle, priority, sound):
        ''' Internal function for sending push message'''

        data = {'token': self.token, 'user': self.username}
        if message:
            data.update({'message': message})
        else:
            data.update({'message': self.message})
        if targetservice:
            data.update({'service': targetservice})
        else:
            if self.targetservice:
                data.update({'service': self.targetservice})
        if title:
            data.update({'title': title})
        else:
            if self.title:
                data.update({'title': self.title})
        if url:
            data.update({'url': url})
        else:
            if self.url:
                data.update({'url': self.url})
        if urltitle:
            data.update({'url_title': urltitle})
        else:
            if self.urltitle:
                data.update({'url_title': self.urltitle})
        if priority:
            data.update({'priority': priority})
        else:
            if self.priority:
                data.update({'priority': self.priority})
        if sound:
            data.update({'sound': sound})
        else:
            if self.sound:
                data.update({'sound': self.sound})
        #print "Request: ", data
        msgdata = urllib.urlencode(data)
        #print msgdata
        _res = urllib2.urlopen(self.pushurl, msgdata).read()
        if not _res:
            raise Exception("Empty response")
        res = json.loads(_res)
        if not res:
            raise Exception("Invalid json response: %s" % _res)
        #print "Response: ", res
        if res['status'] == 1:
            return True
        else:
            return False

