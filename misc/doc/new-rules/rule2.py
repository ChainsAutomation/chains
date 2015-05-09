from definition import Event, Action
import time

def rule(context):
    yield Event(device='tellstick', key='switch-2', data='*')
    Action(device='2-tellstick', action='on', params=['lamp-3'])
