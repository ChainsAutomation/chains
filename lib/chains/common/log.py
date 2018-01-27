# py3: Done
from __future__ import print_function
from __future__ import absolute_import
import logging, logging.handlers
from chains.common.config import CoreConfig
import types, json, os


level = None
logger = None
config = CoreConfig()


def setLevel(_level):
    if not logger:
        return
    levels = {
        'notice': 5,
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
    setFilePath(config.get('logdir') + '/' + name + '.log')


def setFilePath(path):
    fileHandler = logging.handlers.RotatingFileHandler(path, maxBytes=1024 * 1024 * 10, backupCount=2)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.removeHandler(consoleHandler)


def notice(*args):
    msg = formatMessage(args)
    # logger.debug(msg)
    logger.log(5, 'NOTICE: %s' % msg)


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
    # if type(arg) == types.InstanceType:
    if isinstance(arg, types.InstanceType):
        return '%s' % arg.__dict__
    elif type(arg) in [bytes, str]:
        return arg
    elif type(arg) == list:
        result = []
        for item in arg:
            result.append(formatMessageItem(item))
        try:
            return json.dumps(result)
        except TypeError:
            return '%s' % (arg,)
    else:
        try:
            return json.dumps(arg)
        except TypeError:
            return '%s' % (arg,)


# can pass f.ex. __name__ to getLogger() to get per-module logmsgs,
# but we don't initialize logger from inside modules
logger = logging.getLogger()

# Start with a basic print-to-console handler

consoleHandler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s   %(levelname)-10s %(name)-20s %(message)s')
formatter = logging.Formatter('%(asctime)s   %(levelname)-10s %(message)s')
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


level = config.get('loglevel')
setLevel(level)


if __name__ == '__main__':
    print('loglevel: %s' % level)
    debug('debug')
    info('info')
    warn('warn')
    error('error')
