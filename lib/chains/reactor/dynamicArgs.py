import re, copy

TYPE_STR          = type('')
TYPE_TUP          = type((1,))
RESOLVABLE_TYPES  = [TYPE_TUP, TYPE_STR]
DYNAMIC_PATTERN   = re.compile('.*(\$\!?[a-zA-Z0-9_\.]+).*')

def resolveArgs(args, state, State):
    return resolveArg(args, state, State)

def resolveArg(arg, state, State):
    arg = copy.copy(arg)
    if type(arg) == type({}):
        for k in arg:
            arg[k] = resolveArg(arg[k], state, State)
        return arg
    elif type(arg) == type([]):
        arg2 = []
        for a in arg:
            arg2.append(resolveArg(a, state, State))
        return arg2
    elif type(arg) == TYPE_TUP:
        return resolveArgValue(arg, state, State)
    elif type(arg) not in RESOLVABLE_TYPES:
        return arg
    n = 0
    while 1:
        match = DYNAMIC_PATTERN.match(arg)
        if not match:
            break
        key = match.group(1) # f.ex. $hello.world
        # arg is entire param - all value types supported
        if key == arg:
            arg = resolveArgValue(key[1:], state, State)
            break
        # arg is inside param - value is always converted to stirng
        else:
            arg = arg.replace(key, '%s' % resolveArgValue(key[1:], state, State))
            if n > 10000:
                raise Exception('Infinite loop in resolveArg?: %s : %s' % (arg,key))
        n += 1
    return arg

def resolveArgValue(key, state, State):
    if type(key) == type((1,)):
        func = getattr(FUNCTIONS, key[0])
        args = resolveArgs(key[1], state, State)
        return func(*args)
    tmp = key.split('.')
    v = state
    neg = False
    if tmp[0][0] == '!':
        neg = True
        tmp[0] = tmp[0][1:]
    if tmp[0] == 'State':
        sdev = tmp[1]
        skey = tmp[2]
        tmp = tmp[3:]
        v = State.get('%s.%s' % (sdev,skey))
    if v:
        for k in tmp:
            if v == None:
                break
            try: v = v[k]
            except KeyError: v = None
    else:
        v = None

    if neg:
        if v == '0' or v == None: v = False
        v = not v
    return v

class Functions:
    def multiply(self, a, b):
        try: return float(a)*float(b)
        except: return 0

    def add(self, a, b):
        try: return float(a)+float(b)
        except: return 0

FUNCTIONS         = Functions()
