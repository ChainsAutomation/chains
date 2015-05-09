from definition import Event, Action
import time

def rule(context):
    yield Event(device='tellstick', key='switch-2', data='*')
    Action(device='1-tellstick', action='on', params=['lamp-1'])
    #if context.state['timer.hour.data.value'] < 16:
    #    return
    Action(device='1-tellstick', action='on', params=['lamp-2'])
    yield Event(device='tellstick', key='lamp-3', data='*')
