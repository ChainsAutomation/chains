from chains.reactor.definition import Event
import time

def rule(context):
    yield Event(device='tellstick', key='switch-1', data='*')
    time.sleep(0.3)
    if context.test.has_key('event-3.1-seen'):
        context.test['event-3.1-seen'] += 1
    else:
        context.test['event-3.1-seen'] = 1
    yield Event(device='tellstick', key='switch-2', data='*')
    if context.test.has_key('event-3.2-seen'):
        context.test['event-3.2-seen'] += 1
    else:
        context.test['event-3.2-seen'] = 1
