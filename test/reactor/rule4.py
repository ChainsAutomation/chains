from chains.reactor.definition import Event
import time

def rule(context):
    event = yield Event(service='tellstick', key='switch-1', data='*')
    context.test['matched-event'] = event
