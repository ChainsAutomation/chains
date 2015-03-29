import types, re, inspect
import chains.common.jsonlib as json
from chains.common import log

def describeMethods(obj, prefix=None):
    '''
    Analyze all the functions in an object and
    provide a nice list of functions with description,
    list of parameters etc.

    Basically this provides all the info that's needed
    in the actions section of onDescribe.

    Stuff that cannot be analyzed directly from the code
    (like method description, valid parameter values etc.),
    is handeled by analyzing the function comment and looking
    for annotation-like stuff in there. See the _test class
    below for an example of how to write proper comments
    that this function can parse.
    '''
    ret = []
    for k in dir(obj):
        if prefix:
            if k[:len(prefix)] != prefix:
                continue
        fun = getattr(obj, k)
        item = describeMethod(fun)
        if item:
            ret.append(item)
    return ret

def describeMethod(fun):
        if type(fun) != types.MethodType:
            return

        inspection = inspect.getargspec(fun)

        #args = fun.func_code.co_varnames
        #defaults = fun.func_defaults
        args = inspection.args
        defaults = inspection.defaults
        if not defaults: defaults = []
        funcDoc, argsDoc, argsDocOrder = _parseMethodDoc(fun.__doc__)

        item = {
            'name': re.sub( '^action_', '', fun.func_name ),
            'args': [],
            'info': funcDoc
        }
        offset = len(args)-len(defaults)
        for i in range(len(args)):
            if i == 0: # skip 'self'
                continue
            key = args[i]
            if argsDoc.has_key(key):
                arg = argsDoc[key]
            else:
                arg = {}
            arg['key'] = key
            arg['required'] = True
            arg['default'] = None
            if i >= offset:
                arg['required'] = False
                arg['default'] = defaults[i-offset]
            for k in ['type','info','valid']:
                if not arg.has_key(k):
                    arg[k] = None
            item['args'].append(arg)

        if not item['args'] and argsDoc:
            for key in argsDocOrder:
                item['args'].append(argsDoc[key])

        return item


def _parseMethodDoc(text):
    funcDoc = []
    argsDoc = {}
    argsOrder = []
    if text:
        pat = re.compile(' +')
        text = text.strip()
        for line in text.split('\n'):
            line = line.strip()
            tmp = pat.split(line)
            pre = tmp.pop(0)
            if pre and pre[0] == '@':
                pre = pre[1:]
                if pre == 'param':
                    key = tmp.pop(0)
                    argsOrder.append(key)
                    if not argsDoc.has_key(key):
                        argsDoc[key] = {}
                    argsDoc[key]['key'] = key
                    argsDoc[key]['type'] = tmp.pop(0)
                    argsDoc[key]['info'] = ' '.join(tmp)
                    argsDoc[key]['required'] = True
                elif pre == 'valid':
                    key = tmp.pop(0)
                    if not argsDoc.has_key(key):
                        argsDoc[key] = {}
                    argsDoc[key]['valid'] = json.decode(' '.join(tmp))
                elif pre == 'optional':
                    key = tmp.pop(0)
                    if not argsDoc.has_key(key):
                        argsDoc[key] = {}
                    argsDoc[key]['required'] = False
            else:
                funcDoc.append(line)
    return ('\n'.join(funcDoc), argsDoc, argsOrder)

def _test():
    class MyObj:
        def cmdFunc1(self, arg1, arg2=1):
            """ A function that does something clever """
            print 'hei1'
        def cmdFunc2(self, arg1, kw1=23):
            """
            A function that does something more clever.
            @param arg1 string Some string lizm...
            @param kw1  int   Some int parameter.
            @valid kw1  [0,1,2]
            """
            dummyvar = 1
            print 'hei2'
        def cmdFunc3(self):
            print 'hei3'
    o = MyObj()
    data = describeMethods(o)
    #print data
    print ''
    for item in data:
        print '%-20s %s' % (item['name'], item['info'])
        print '    %-15s  %-10s  %-5s  %-10s %-20s %s' % ('ARG','TYPE','REQ','DEF','VALID','INFO')
        for a in item['args']:
            print '    %-15s  %-10s  %-5s  %-10s %-20s %s' % (a['key'],a['type'],a['required'],a['default'],a['valid'],a['info'])
        print ''

if __name__ == '__main__':
    _test()
