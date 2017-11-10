from chains.service import Service
from chains.common import log, config
import os, copy, datetime, time, logging, logging.handlers

class LogService(Service):

    SELF_LOG = '__self__'

    def onInit(self):
        self.loggers = {}
        self.logdir = ''
        try:
            self.logdir = self.config.get('logdir')
            log.info('Using logdir from config: %s' % self.logdir)
        except KeyError:
            self.logdir = '/var/log/chains'
            log.warn('Got no logdir in config, using %s' % self.logdir)

    def action_log(self, message, file=None, *args):
        """
        Log a message to file
        @param   message   string   Text to log
        @param   file      string   File identifier, refereing to an item under [files] in config.
        @param   args      list     List of values to expand into message (optional)
        """
        if args and len(args) > 0:
            message = message % args
        if not file:
            file = self.config.get('defaultfile')
        key = None
        if file != self.SELF_LOG and file[0] != '/':
            try:
                key = file
                files = self.config.data('files')
                file = files[file]
                if file[0] != '/':
                    file = '%s/%s' % (self.logdir, file)
            except KeyError:
                raise Exception("No such configfile. You may need to add %s under %s service's config section [files]" % (file, self.config.get('id')))
        self._log(file, message, key)

    def _log(self, file, message, key):
        if file == self.SELF_LOG:
            log.info(message)
        else:
            file = '%s.log' % file
            logger2 = self.getLogger(file, key)
            logger2.info(message)

    def getLogger(self, file, key):
        if not self.loggers.has_key(file):
            formatter = logging.Formatter('%(asctime)s   %(message)s')
            fileHandler = logging.handlers.RotatingFileHandler(file, maxBytes=1024*1024*10, backupCount=2)
            fileHandler.setFormatter(formatter)
            self.loggers[file] = logging.getLogger('chains-%s' % key)
            self.loggers[file].addHandler(fileHandler)
        return self.loggers[file]

