from __future__ import absolute_import
from __future__ import print_function
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
                    pkgName=formatterName,  # 'chains.commandline.formatter.%s' % formatterName,
                    className='Formatter%s' % formatterName,
                    path='%s/%s.py' % (dir, formatterName)
                )
            except ImportError:
                pass
    raise Exception('Formatter not found: %s' % formatterName)


def getFormatterDirs():
    dirs = []

    # If user has configured custom commands dir
    customDirs = config.data('commandline.commands')
    if customDirs:
        for customDir in customDirs:
            if os.path.exists(customDir):
                dirs.append(customDir + '/formatter')

    # Build in commands
    dirs.append(config.get('libdir') + '/commandline/formatter')

    return dirs
