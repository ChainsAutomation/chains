from chains.reactor.definition import Event

def rule(context):
    yield Event(service='tellstick', key='switch-2', data='*')
    if context.test.has_key('event-1.1-seen'):
        context.test['event-1.1-seen'] += 1
    else:
        context.test['event-1.1-seen'] = 1
