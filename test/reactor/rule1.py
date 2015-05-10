from chains.reactor.definition import Event

def rule(context):
    yield Event(device='tellstick', key='switch-2', data='*')
    context.test['event-seen'] = True
