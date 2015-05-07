from definition import Event, Action
import time

def rule(context):
    yield Event(device='tellstick', key='switch-2', data='*')
    time.sleep(3) # block!
    Action(device='tellstick', action='on', params=['lamp-1'])
    if context.state['timer.hour.data.value'] < 16:
        return
    Action(device='tellstick', action='on', params=['lamp-2'])
    yield Event(device='tellstick', key='none')
