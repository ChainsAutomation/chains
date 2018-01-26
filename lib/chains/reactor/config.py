from __future__ import absolute_import
from __future__ import print_function
from chains.common.config import CoreConfig
from chains.common import ParameterException, ChainsException, log, utils
import os

config = CoreConfig()

# todo: tests
# todo: cleanup


def enable(rule):
    if not rule:
        raise ParameterException('Missing rule')
    src = _getAvailableFile(rule)
    dst = _getEnabledFile(rule)
    if not os.path.exists(src):
        raise NoSuchRuleException(rule)
    if os.path.exists(dst):
        raise RuleAlreadyEnabledException(rule)
    os.symlink(src, dst)


def disable(rule):
    if not rule:
        raise ParameterException('Missing rule')
    src = _getAvailableFile(rule)
    dst = _getEnabledFile(rule)
    if not os.path.exists(src):
        raise NoSuchRuleException(rule)
    if not os.path.exists(dst):
        raise RuleAlreadyDisabledException(rule)
    os.unlink(dst)
    dst += 'c'  # .pyc
    if os.path.exists(dst):
        os.unlink(dst)


def getEnabledNames():
    return _dirRules(_getEnabledDir())


def getAvailableNames():
    return _dirRules(_getAvailableDir())


def getData(module=None):
    _addRulesPath()
    mods = getEnabledNames()
    # print 'MODS: %s' % mods
    if not mods:
        return []
    pkg = __import__(_getEnabledModule())
    reload(pkg)
    ret = []
    for modname in mods:
        if module and module != modname:
            continue
        try:
            pkg2 = __import__('%s.%s' % (_getEnabledModule(), modname))
            reload(pkg2)
            mod = getattr(pkg2, modname)
            reload(mod)
            conf = {'id': modname, 'maxCount': 1}  # todo: config in rule with maxCount etc
            ret.append((mod, conf))
        except Exception as e:
            log.error('Skip invalid rule: %s : %s' % (modname, utils.e2str(e)))
    return ret


def _getEnabledFiles():
    ret = []
    for f in _getRuleFiles():
        if f[1]:
            ret.append(f[0])
    return ret


def _getAvailableFiles():
    ret = []
    for f in _getRuleFiles():
        if not f[1]:
            ret.append(f[0])
    return ret

def _getEnabledFile(rule):
    return '%s/%s.py' % (_getEnabledDir(), rule)


def _getAvailableFile(rule):
    return '%s/%s.py' % (_getAvailableDir(), rule)


def _getEnabledModule():
    return 'rules_enabled'


def _getAvailableModule():
    return 'rules_available'


def _getEnabledDir():
    p = _getRulesPath() + '/' + _getEnabledModule()
    _makeDirWithInitFile(p)
    return p


def _getAvailableDir():
    p = _getRulesPath() + '/' + _getAvailableModule()
    if not os.path.exists(p):
        os.makedirs(p)
    return p


def _getRuleFiles():
    _addRulesPath()
    import rules_enabled
    import os
    f = rules_enabled.__file__.split('/')
    f.pop()
    f = '/'.join(f)
    ret = []
    ena = []
    for fi in os.listdir(f):
        ena.append(fi)
        if fi[0] == '_':
            continue
        fi = fi.split('.')
        if fi.pop() != 'py':
            continue
        fi = '.'.join(fi)
        ret.append((fi, True))
    f = f.split('/')
    f.pop()
    f.append('rules_available')
    f = '/'.join(f)
    for fi in os.listdir(f):
        if fi in ena:
            continue
        if fi[0] == '_':
            continue
        fi = fi.split('.')
        if fi.pop() != 'py':
            continue
        fi = '.'.join(fi)
        ret.append((fi, False))
    ret.sort()
    return ret


def _getRulesPath():
    d = config.get('rulesdir')
    if not d:
        raise Exception('Must configure main.rulesdir in chains.conf')
    if not os.path.exists(d):
        raise Exception('No such rulesdir: %s' % d)
    return d


def _addRulesPath():
    d = _getRulesPath()
    import sys
    for f in sys.path:
        if f == d:
            return  # already set
    sys.path.append(d)


def _makeDirWithInitFile(p):
    if not os.path.exists(p):
        os.makedirs(p)
    initf = '%s/__init__.py' % p
    if not os.path.exists(initf):
        with open(initf, 'w') as fp:
            fp.write('')


def _dirRules(dir):
    ret = []
    for f in os.listdir(dir):
        if f == '__init__.py':
            continue
        if f == 'ruleconfig.py':
            continue
        tmp = f.split('.')
        ext = tmp.pop()
        if ext != 'py':
            continue
        ret.append('.'.join(tmp))
    return ret


class NoSuchRuleException(ChainsException):
    pass


class RuleAlreadyEnabledException(ChainsException):
    def __init__(self, rule):
        ChainsException.__init__(self, 'Rule already enabled: %s' % rule)
        self.rule = rule


class RuleAlreadyDisabledException(ChainsException):
    def __init__(self, rule):
        ChainsException.__init__(self, 'Rule already disabled: %s' % rule)
        self.rule = rule


if __name__ == '__main__':

    # try: disable('event_log')
    # except: pass

    print('getEnabledNames (dir: %s):' % (_getEnabledDir()))
    for f in getEnabledNames():
        print('   %s' % f)
    print('getRulesAvailable (dir: %s):' % (_getAvailableDir()))
    for f in getAvailableNames():
        print('   %s' % f)
    print('getData:')
    for r in getData():
        print('  %s' % (r,))

    """
    print ''
    print 'enable rule: event_log'
    enable('event_log')
    print ''

    print 'getEnabledNames (dir: %s):' % (_getEnabledDir())
    for f in getEnabledNames():
        print '   %s' % f
    print 'getRulesAvailable (dir: %s):' % (_getAvailableDir())
    for f in getAvailableNames():
        print '   %s' % f
    print 'getData:'
    for r in getData():
        print '  %s' % (r,)

    print ''
    print 'disable rule: event_log'
    disable('event_log')
    print ''
    """
