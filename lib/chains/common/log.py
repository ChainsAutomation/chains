# vim: tabstop=4 shiftwidth=4 sts=4 bg=dark expandtab

import logging, logging.handlers
from chains.common import config


level  = None
logger = None

def setLevel(_level):
    if not logger: return
    levels = {
        'notice': logging.DEBUG,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR
    }
    logger.setLevel(levels[_level])
    global level
    level = _level

def getLevel():
    global level
    return level

def setFileName(name):
    setFilePath( config.get('logdir') + '/' + name + '.log' )

def setFilePath(path):
    fileHandler = logging.handlers.RotatingFileHandler(path, maxBytes=1024*1024*10, backupCount=2)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.removeHandler(consoleHandler)

def notice(o):
    logger.debug(o)
def debug(o):
    logger.debug(o)
def info(o):
    logger.info(o)
def warn(o):
    logger.warn(o)
def error(o):
    logger.error(o)
def query(q, a):
    raise Exception('deprecated')


# can pass f.ex. __name__ to getLogger() to get per-module logmsgs,
# but we don't initialize logger from inside modules
logger = logging.getLogger()

# Start with a basic print-to-console handler

consoleHandler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s   %(levelname)-10s %(name)-20s %(message)s')
formatter = logging.Formatter('%(asctime)s   %(levelname)-10s %(message)s')
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


level = config.get('loglevel')
setLevel(level)


if __name__ == '__main__':
    print 'loglevel: %s' % level
    debug('debug')
    info('info')
    warn('warn')
    error('error')

