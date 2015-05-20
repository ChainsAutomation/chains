from chains.reactor.definition import Event
import time

def rule(context):
    event = yield Event(device='tellstick', key='switch-1', data='*')
    context.test['matched-event'] = event
