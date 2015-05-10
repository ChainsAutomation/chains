# vim: tabstop=4 shiftwidth=4 sts=4 bg=dark expandtab

import logging, logging.handlers
from chains.common import config
import types, json, os


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
    if not os.path.exists(config.get('logdir')):
        os.makedirs(config.get('logdir'))
    setFilePath( config.get('logdir') + '/' + name + '.log' )

def setFilePath(path):
    fileHandler = logging.handlers.RotatingFileHandler(path, maxBytes=1024*1024*10, backupCount=2)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.removeHandler(consoleHandler)

def notice(*args):
    msg = formatMessage(args)
    logger.debug(msg)
def debug(*args):
    msg = formatMessage(args)
    logger.debug(msg)
def info(*args):
    msg = formatMessage(args)
    logger.info(msg)
def warn(*args):
    msg = formatMessage(args)
    logger.warn(msg)
def error(*args):
    msg = formatMessage(args)
    logger.error(msg)

def formatMessage(args):
    result = []
    for arg in args:
        result.append(formatMessageItem(arg))
    return ' '.join(result)

def formatMessageItem(arg):
    if type(arg) == types.InstanceType:
        return '%s' % arg.__dict__
    elif type(arg) in [types.StringType, types.UnicodeType]:
        return arg
    else:
        return json.dumps(arg)


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

