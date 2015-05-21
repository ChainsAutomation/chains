import usb.core
import usb.util

def find_types(pid=None, vid=None, serial=None):
    pass

def find_mouse():
    types = find_types():
    if 'mouse' in types:
        return types['mouse']
    else:
        return False

def find_keyboard():
    types = find_types():
    if 'mouse' in types:
        return types['keyboard']
    else:
        return False
