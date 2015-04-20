import chains.reactor.rules.functions as _functions
from chains.reactor.rules.functions import StopRuleException

def cc(id, **kw):
	kw['id'] = id
	return ('c', kw)

def evt(device, key, value='*', operator=None, extra=None, target=None, timeout=None, onTimeout=None):
    return ('e', device, key, value, operator, extra, target, timeout, onTimeout)

def sevt(device, key, value=None, extra=None, eventType='d'):
    event = {'device': device, 'key': key, 'value': value, 'extra': {}}
    if extra: evt['extra'] = extra

    return fun(_functions.sendEvent, event, eventType)

def act(devid, action, args=None, target=None, block=None, timeout=None):
    return ('a', devid, action, args, target, block, timeout)

def fun(func, args=None, target=None):
    if not args: args = {}
    return ('f', func, args, target)

def iff(key, value, operator='='):
    return fun(_functions.iff, {'key': key, 'value': value, 'operator': operator})

""" DEPRECATED

def pevt(port, *args, **kw):
    port = list(port)
    for a in args:
        port.append(a)
    return evt(*port, **kw)

def port(devid, key, type=None):
    if not type: type = 'int'
    return (devid, key)

def startseq(seqid, preset):
    return ('s', seqid, preset)

def stopseq(seqid, preset, wait=False):
    return ('S', seqid, preset, wait)

def mact(action, args=None, target=None):
    return act('master', action, args, target)

class novalue:
    pass

"""

# Test
if __name__ == '__main__':
    rule = [
        cc(id='event_log', info='Log all events in compact format'),
        evt('*', '*', '*', target='var'),
        act('log', 'log', ['$var.device $var.key = $var.value', 'event'])
    ]
    for line in rule:
        print line
