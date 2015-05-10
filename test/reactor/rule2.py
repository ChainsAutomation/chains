from chains.reactor.definition import Event

def rule(context):
    yield Event(device='tellstick', key='switch-1', data='*')
    context.test['event1-seen'] = True
    yield Event(device='tellstick', key='switch-2', data='*')
    context.test['event2-seen'] = True
    if context.state.get('timer.hour.data.value') < 16:
        return
    yield Event(device='tellstick', key='switch-3', data='*')
    context.test['event3-seen'] = True

def onComplete(context):
    context.test['complete'] = True
