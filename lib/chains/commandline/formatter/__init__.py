from chains.common import utils
from chains.common.config import CoreConfig
import os

config = CoreConfig()

class Formatter:
    pass

def load(formatterName):
    formatterName = utils.ucfirst(formatterName)
    for dir in getFormatterDirs():
        path = '%s/%s.py' % (dir, formatterName)
        if os.path.exists(path):
            try:
                return utils.newObject(
                    pkgName   = formatterName, #'chains.commandline.formatter.%s' % formatterName, 
                    className = 'Formatter%s' % formatterName,
                    path = '%s/%s.py' % (dir, formatterName)
                )
            except ImportError:
                pass
    raise Exception('Formatter not found: %s' % formatterName)

def getFormatterDirs():
    dirs = []

    # If user has configured custom commands dir
    items = config.data('commandline')
    if items:
        for key in items:
            tmp = key.split('.')
            if len(tmp) == 2 and tmp[0] == 'commands':
                dirs.append( items[key] + '/formatter' )

    # Build in commands
    dirs.append( config.get('libdir') + '/commandline/formatter' )

    return dirs
