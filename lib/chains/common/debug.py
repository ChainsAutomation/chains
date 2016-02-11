from __future__ import print_function
from functools import wraps

def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_str = "(" + ", ".join(map(str, args)) + ", " + str(kwargs) + ")"
        print("debug: " + func.__name__ + args_str)
        return func(*args, **kwargs)
    return wrapper
