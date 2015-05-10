from chains.reactor.definition import Event
import time

def rule(context):
    yield Event(device='tellstick', key='switch-1', data='*')
    time.sleep(0.5)
    context.test['event1-seen'] = True
    yield Event(device='tellstick', key='switch-2', data='*')
    context.test['event2-seen'] = True
