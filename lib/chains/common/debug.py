from __future__ import print_function
from __future__ import absolute_import
from functools import wraps
import inspect
from six.moves import map
import sys

def debug_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        PY3 = sys.version_info[0] == 3
        if PY3:
        # inspect.signature only available in py3
            print('debug: ' + func.__name__ + str(inspect.signature(func)))
        args_str = "(" + ", ".join(map(str, args)) + ", " + str(kwargs) + ")"
        print("debug: " + func.__name__ + args_str)
        return func(*args, **kwargs)
    return wrapper

@debug_decorator
def _test(arg1, arg2, kw1='something', kw2='stuff'):
    print('This is all I do')

if __name__ == '__main__':
    _test('hi', 'guy', kw1='something_or_other', kw2='stuff_yo')
