from chains.common import log

class StopRuleException(Exception):
    pass

def sendEvent(event, eventType):
    conn      = amqp.Connection()
    rpc       = conn.rpc()

    result = rpc.call('%se.%s.%s' % (eventType, device, key), [event])
    log.debug("Reactor sent and got result: %s" % (result,))


def iff(context, args):
    op = '='
    try: op = args['operator']
    except: pass
    res = False
    v1 = args['key']
    v2 = args['value']
    if op in ['=','!=']:
        if v1 == 'True': v1 = True
        if v1 == 'False': v1 = False
        if v2 == 'True': v2 = True
        if v2 == 'False': v2 = False
        if v1 == 'None': v1 = None
        if v2 == 'None': v2 = None

        #if op == '=':
        if type(v1) == type(v2):
            if v1 == v2: res = True
        else:
            if v1 in [True,False] and type(v2) in [type(1),type(0.0),type('')]:
                if v1:
                    if v2 in [1,'1','1.0','True','yes','on']: res = True
                    #else: res = False
                else:
                    if v2 in [0,'0','0.0','False','no','off','']: res = True
                log.debug('BOOL-IF1: %s | %s | res:%s' % (v1, v2, res))
            elif v2 in [True,False] and type(v1) in [type(1),type(0.0),type('')]:
                if v2:
                    if v1 in [1,'1','1.0','True','yes','on']: res = True
                else:
                    if v1 in [0,'0','0.0','False','no','off','']: res = True
                log.debug('BOOL-IF2: %s | %s | res:%s' % (v1, v2, res))
            elif type(v1) in [type(1),type(0.0)] and type(v2) in [type(1),type(0.0),type('')]:
                v1 = float(v1)
                v2 = float(v2)
                if abs(v1-v2) < 0.0000000001: res = True
                log.debug('NUM-IF1: %s | %s | res:%s' % (v1, v2, res))
            elif type(v2) in [type(1),type(0.0)] and type(v1) in [type(1),type(0.0),type('')]:
                v1 = float(v1)
                v2 = float(v2)
                if abs(v1-v2) < 0.0000000001: res = True
                log.debug('NUM-IF2: %s | %s | res:%s' % (v1, v2, res))
            elif v1 == None:
                if ('%s'%v2) in ['0','False','None','']:
                    res = True
                log.debug('NONE-IF1: %s | %s | res:%s' % (v1, v2, res))
            elif v2 == None:
                if ('%s'%v1) in ['0','False','None','']:
                    res = True
                log.debug('NONE-IF2: %s | %s | res:%s' % (v1, v2, res))
            else:
                v1 = '%s' % v1
                v2 = '%s' % v2
                if v1 == v2: res = True
                log.debug('STRFALL-IF: %s | %s | res:%s' % (v1, v2, res))
        #else:
        #    if v1 != v2: res = True
        if op == '!=':
            res = not res

    elif op == '>' or op == '<':
        try: v1 = float(v1)
        except: v1 = None
        try: v2 = float(v2)
        except: v2 = None
        if v1 == None and v2 == None: return False
        if v1 == None: v1 = 0
        if v2 == None: v2 = 0
        if op == '<' and v1 < v2:
            res = True
        if op == '>' and v1 > v2:
            res = True
    log.info('IF: ( %s %s |%s| %s %s ) = %s' % (type(v1), v1, op, type(v2), v2, res))
    if not res:
        raise StopRuleException('Nomatch')
