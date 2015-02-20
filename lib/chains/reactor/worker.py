from chains.common import log, utils, amqp
from chains.reactor.rules.functions import StopRuleException
import chains.reactor.rules.config
import time, os, copy, re, threading

def fixnum(v):
    try: return float(v)
    except: return 0

class Worker:

    def __init__(self, reactor):

        self.busy               = True

        self.reactor            = reactor
        self.connection         = amqp.Connection()

        self.timers             = {}
        self.lastdelete         = 0
        self.deleteinterval     = 30
        self.eventValuePattern  = re.compile('(.*)\*(.*)')
        self.cid                = 0
        self.activeChains       = {}

        self.chains             = self.loadRules()
        self.busy               = False

    def loadRules(self):
        # Reload config module to make sure we have fresh rules
        reload(chains.reactor.rules.config)

        # Load all rules from rules_enabled/ into an array
        chains1 = chains.reactor.rules.config.getData()

        # Make into a hash keyed on chain id
        # And get config from cc() directive
        chains2 = {}
        for cnum in range(len(chains1)):
            chain = chains1[cnum]
            conf = {}
            # Look for cc() directive
            for i in range(len(chain)):
                part = chain[i]
                if part[0] == 'c':
                    if len(part) < 2:
                        log.error("got 'c' item of len < 2! %s" % (part,))
                    else:
                        conf = part[1]
                    del chain[i]
                    break
            # Use id from cc() or a dummy if no id found
            cid = 'noid-%s' % cnum
            if conf and conf.has_key('id'): cid = conf['id']
            # Disallow duplicate ids
            if chains2.has_key(cid):
                raise Exception('Multiple chains with id: %s' % cid)
            # Populate chains hash
            chains2[cid] = {'chain': chain, 'conf': conf}
        return chains2

    def get(self, cid):
        data = self.list(thecid=cid)
        if not data: return None
        data[0]['chain'] = self.chains[cid]['chain']
        return data[0]

    def list(self, file=None, thecid=None):
        ret = []
        for cid in self.chains:
            if thecid and cid != thecid: continue
            if file and self.chains[cid]['conf']['module'] != file: continue
            item = copy.copy(self.chains[cid]['conf'])
            item['active'] = []
            item['length'] = len(self.chains[cid]['chain'])
            for acid in self.activeChains:
                ac = self.activeChains[acid]
                if ac['id'] == cid:
                    ac2 = {
                        'id': acid,
                        'step': ac['step'],
                        'atime': ac['atime'],
                        'etime': ac['etime'],
                        'next': None,
                    }
                    if (len(ac['chain']) > 0):
                        ac2['next'] = ac['chain'][0]
                    item['active'].append(ac2)
            item['id'] = cid
            ret.append(item)
        return ret

    def getActiveChainOnTimeout(self, acid):
        try: return self.activeChains[acid]['conf']['onTimeout']
        except KeyError: return None

    def getActiveChainTimeout(self, acid):
        return self.getChainTimeout( self.activeChains[acid]['id'] )

    def getChainTimeout(self, cid):
        conf = self.chains[cid]['conf']
        if conf.has_key('timeout') and conf['timeout']:
            return float(conf['timeout'])
        else:
            return None

    def getChainOnTimeout(self, cid):
        conf = self.chains[cid]['conf']
        if conf.has_key('onTimeout') and conf['onTimeout']:
            return conf['onTimeout']
        else:
            return None

    def getActiveChainLastTime(self, acid):
        ac = self.activeChains[acid]
        t = float(ac['atime'])
        if float(ac['etime']) > t:
            t = float(ac['etime'])
        return t

    # Return:
    #   False       if not timed out yet or no timeouts configured
    #   True        if timed out and should be deleted
    #   None        if timed out and chain has been replaced by ontimeout, should not be deleted
    def checkTimeouts(self, acid, nextEvent):

        chainTimeout = self.getActiveChainTimeout(acid)
        eventTimeout = None
        if len(nextEvent) > 7:
            eventTimeout = nextEvent[7]
        if not eventTimeout and not chainTimeout:
            return False

        cid = self.activeChains[acid]['id']
        elapsed = time.time() - self.getActiveChainLastTime(acid)
        chainOnTimeout = self.getActiveChainOnTimeout(acid)
        eventOnTimeout = None
        if len(nextEvent) > 7:
            eventOnTimeout = nextEvent[8]
        eventOnTimeoutType = 'event'
        if not eventOnTimeout and chainOnTimeout:
            eventOnTimeout = chainOnTimeout
            eventOnTimeoutType = 'chain'

        # Check event and chain timeouts
        for (timeout,onTimeout,isEvent) in [(eventTimeout,eventOnTimeout,True), (chainTimeout,chainOnTimeout,False)]:
            typ = 'chain'
            if isEvent: typ = 'event'
            otyp = 'chain'
            if isEvent: otyp = eventOnTimeoutType
            if not timeout or elapsed < timeout:
                continue
            if onTimeout:
                log.info('Chain %s (%s) elapsed time %s reached %s-timeout %s, action: run %s-onTimeout' % (acid, cid, elapsed, typ, timeout, otyp))
                # Replace current chain with onTimeout chain
                self.activeChains[acid]['chain'] = copy.copy(onTimeout)
                self.activeChains[acid]['etime'] = time.time()
                # Delete chainwide timeout if that's what we're running, or will run forever
                if not isEvent or eventOnTimeoutType == 'chain':
                    del self.activeChains[acid]['conf']['onTimeout']
                # Send (any) event to make sure next step in onTimeout chains will run if apropriate
                try:
                    self.app
                    self.app.onEvent({'device': 'dummy', 'key': 'trigger', 'value': 'foo'})
                except AttributeError:
                    log.warn('EventListenerChains got no app (yet?)')
                return None
            else:
                log.info('Chain %s (%s) elapsed time %s reached %s-timeout %s, action: delete chain' % (acid, cid, elapsed, typ, timeout))
                return True

        return False


    def onEvent(self, event):
        self.timer('onEvent', True)

        # Ensure not ran in paralell
        n = 0
        while self.busy:
            time.sleep(0.1)
            n += 1
            if n > 200: raise Exception('Timeout waiting for busy chains')
        self.busy = True

        # Remove any chains that were completed last run
        self.delDoneChains()

        # Check all chains that have been activated before
        # pop off event if matched (actions will be executed below).
        for acid in self.activeChains:
            c = self.activeChains[acid]['chain']
            # Chains currently running action(s) should be left alone
            if self.activeChains[acid]['thread'] and self.activeChains[acid]['thread'].busy:
                continue
            # Ditto for completed chains that are not removed yet
            if self.activeChains[acid]['done']:
                continue
            # End of chain
            if len(c) == 0:
                self.activeChains[acid]['done'] = 'endofchain'
                continue
            # Check chain and event timeouts
            res = self.checkTimeouts(acid, c[0])
            if res == True: # timeout
                self.activeChains[acid]['done'] = 'timeout'
                continue
            if res == None: # ontimeout
                continue
            if self.matchEvent(c[0], event, acid, False, self.activeChains[acid]['state']):
                log.info("Matched event in active chain %s (%s): %s" % (acid, self.activeChains[acid]['id'], c[0]))
                self.activeChains[acid]['etime'] = time.time() # remember last event time for timeout
                self.activeChains[acid]['step'] += 1
                self.updateState(acid, 'event', event, c[0])
                c.pop(0) # remove event from chain
                self.activeChains[acid]['chain'] = c # needed?

        # Check all configured chains, and activate if we've got a match.
        # Pop off matched event.
        for cid in self.chains:
            c = self.chains[cid]['chain']
            if self.matchEvent(c[0], event, cid, True, {}):
                # Reached maxcount?
                if not self.chains[cid]['conf'].has_key('maxcount') or not self.chains[cid]['conf']['maxcount']:
                    self.chains[cid]['conf']['maxcount'] = 1
                acount = 0
                for acid in self.activeChains:
                    if self.activeChains[acid]['id'] == cid and not self.activeChains[acid]['done']:
                        acount += 1
                if acount >= int(self.chains[cid]['conf']['maxcount']):
                    # todo: change to log.debug
                    log.info("NOT activating config chain %s because maxcount of %s already reached" % (cid, self.chains[cid]['conf']['maxcount']))
                    continue
                # Or active new chain
                c2 = copy.copy(c) # copy, not reference, or we will mess up config
                c2.pop(0)
                # todo: change to log.debug
                self.cid += 1
                log.info("Activate config chain %s as %s" % (cid, self.cid))
                onTimeout = self.getChainOnTimeout(cid)
                self.activeChains[self.cid] = {
                    'chain': c2, # rules
                    'state': {}, 
                    'id': cid,  # chain (config) id
                    'etime': time.time(),  # last event time
                    'atime': 0,  # last action time
                    'step': 1, 
                    'conf': {'onTimeout': onTimeout},
                    'thread': None,
                    'done': False # changed to true when ready to delete
                }
                self.updateState(self.cid, 'event', event, c[0])

        # Check if any active chains has an action as next element(s), and execute it/them
        for cid in self.activeChains:
            # Ignore already running chains
            if self.activeChains[cid]['thread'] and self.activeChains[cid]['thread'].busy:
                continue
            # Ditto for done
            if self.activeChains[cid]['done']:
                continue
            # Run actions in a separate thread
            if self.activeChains[cid]['thread']:
                self.activeChains[cid]['thread'].stop = True
                log.debug('Delete thread: %s : %s' % (cid,self.activeChains[cid]['thread']))
                del self.activeChains[cid]['thread']
            self.activeChains[cid]['thread'] = ChainThread(self, cid, event)
            self.activeChains[cid]['thread'].start()
        self.busy = False
        self.timer('onEvent', False)

    def delDoneChains(self):
        if (time.time()-self.lastdelete) < self.deleteinterval:
            return
        ids = []
        for cid in self.activeChains:
            if self.activeChains[cid]['done']:
                if self.activeChains[cid]['thread'].busy:
                    log.info('Not removing chain %s : %s - because thread is busy' % (cid, self.activeChains[cid]['done']))
                else:
                    ids.append(cid)
        for cid in ids:
            log.info('Remove chain %s : %s' % (cid, self.activeChains[cid]['done']))
            try: 
                del self.activeChains[cid]
            except KeyError: 
                log.info('Ignoring attempt to remove nonexisting active chain: %s' % cid)

    def updateState(self, cid, typ, data, conf=None, key=None): # key=target
        if not key:
            if typ == 'event':
                if len(conf) > 6:
                    key = conf[6]
            elif typ == 'act':
                if len(conf) > 4:
                    key = conf[4]
            else:
                raise Exception('Unknown chain state type: %s' % typ)
        if not key:
            return
        log.debug("Set state %s in chain %s = %s" % (key, cid, data))
        self.activeChains[cid]['state'][key] = data

    # just a wrapper for debugging
    def matchEvent(self, e1, e2, cid, isConfig, state):
        return self._matchEvent(e1, e2, state)
        """
        res = self._matchEvent(e1, e2, state)
        if res:
            txt = "active"
            if isConfig: txt = "config"
            log.debug("Matched event in %s chain %s: dev=%s key=%s val=%s op=%s extra=%s" % (txt, cid, e1[1], e1[2], e1[3], e1[4], e1[5]))
        else:
            #log.debug("Event not matched: %s | %s" % (e1, e2))
            pass
        return res
        """

    # Check if an event item (e1) from a chain
    # matches an incoming event dictionary (e2)
    # Supports wilcard * in device, key, extra, and value (if operator is =)
    def _matchEvent(self, e1, e2, state):

        err = False

        # Device and key must always match (?)
        n = 1
        for k in ['device', 'key']:
            #if str(e1[n]) != str(e2[k]) and str(e1[n]) != '*': # str to match regardless of type
            if not self._matchEventValue(k, e1[n], e2[k], state): 
                #log.debug("Nomatch on %s, expected %s, got %s" % (k, e1[n], e2[k]))
                err = True
                break
            n += 1
        if err: return False

        # Check value with operator
        # @todo: add more operators
        # @todo: add an operator for using a python function, for special cases that cannot be standardized?
        val = e1[3]
        op = e1[4]
        ok = False
        if not op or op == '=':
            if self._matchEventValue('value', val, e2['data']['value'], state): ok = True
        elif op == '>':
            if fixnum(val) > fixnum(e2['data']['value']): ok = True
        elif op == '<':
            if fixnum(val) < fixnum(e2['data']['value']): ok = True
        if not ok: return False


        # Match on key value pairs in event's extra dictionary
        # @todo: use same matching system for extra as for value above (separate function)
        # @todo: recursive matching a'la my.long.key = 3  ==  {'extra':{'my':{'long':{'key':3}}}}
        if e1[5]:
            err = False
            for key in e1[5]:
                val = e1[5][key]
                if not e2.has_key('data') or not e2['data'].has_key(key) or not self._matchEventValue('data.%s' % key, val, e2['data'][key], state):
                    err = True
                    break
            if err: return False

        return True
        

    # Check if an event value (device, key, etc) matches configured chain event value
    # Supports wildcard with * 
    def _matchEventValue(self, key, configVal, eventVal, state):
        dbgType = None
        res = None
        configVal = self.reactor.resolveArgs(configVal, state)
        if configVal and eventVal and configVal != '*' and self.eventValuePattern.match('%s'%configVal):
            dbgType = 'pattern'
            configVal = configVal.replace('*', '.+')
            pat = re.compile(configVal)
            if pat.match('%s'%eventVal):
                res = True
            else:
                res = False
        # Match myEvent = myEvent or myEvent = *
        else:
            if configVal == eventVal or configVal == '*':
                res = True
            else:
                res = False
        return res


    """
    def startSequence(self, seq, preset):
        self.app.onStartSequence(seq, preset)
    def stopSequence(self, seq, preset, wait):
        self.app.onStopSequence(seq, preset)
        ok = True
        if wait:
            timeout = 30
            dly = 0.5
            ok = False
            import time
            for i in range(timeout):
                if not self.app.seq.has_key(seq):
                    ok = True
                    break
                time.sleep(dly)
        return ok
    """

    # what is this? -- profiling i think?

    def timer(self, fun, isStart):
        if isStart:
            self.timers['_%s'%fun] = time.time()
        else:
            if not self.timers.has_key(fun) or len(self.timers[fun]) > 100: self.timers[fun] = []
            self.timers[fun].append( time.time()-self.timers['_%s'%fun] )

    def getTimers(self):
        ret = {}
        for t in self.timers:
            if t[0] == '_': continue
            ret[t] = self.timers[t]
        return ret


# Each active chain has a ChainThread instance for running actions
class ChainThread(threading.Thread):

    def __init__(self, listener, acid, event):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.listener = listener # ChainsListener
        self.reactor = listener.reactor
        self.acid = acid   # active chain id
        self.busy = False  # if running action(s)
        self.event = event
        self.stop = False
        self.actionRpcChannels = {}
        #log.info('NEW ChainThread: %s : %s' % (acid,self))

    def setDone(self, val):
        #log.info('setDone: %s : %s : %s' % (self.acid,val,self))
        self.listener.activeChains[self.acid]['done'] = val

    def getDone(self):
        val = self.listener.activeChains[self.acid]['done']
        #log.info('getDone: %s : %s : %s' % (self.acid,val,self))
        return val

    def run(self):

        # Don't run if already running
        #log.info('run %s' % self.acid)
        if self.getDone(): return
        if self.busy: return
        self.busy = True
        #log.info('RUN ACT %s' % self.acid)

        # Chain may have been deleted by another thread,
        # in which case we're done, so just return.
        cid = self.acid
        try: c = self.listener.activeChains[cid]['chain']
        except KeyError: 
            self.busy = False
            return

        # Reached end of chain?
        if len(c) == 0:
            self.setDone('endofchain')
            self.busy = False
            return

        #kill = False
        num = 0

        # Foreach rule
        for i in range(len(c)):
            if self.stop: return
            typ = c[i][0]
            # Execute normal action?
            if typ == 'a':
                try:
                    block = None
                    timeout = None
                    if len(c[i]) > 5: block = c[i][5]
                    if len(c[i]) > 6: timeout = c[i][6]
                    if block == None:
                        if len(c) > (i+1):
                            block = True
                        else:
                            block = False
                    funres = self.executeAction(c[i], cid, block, timeout)
                    target = None
                    if len(c[i]) > 4: target = c[i][4]
                    if target:
                        self.listener.updateState(cid, 'event', funres, key=target)
                except Exception, e:
                    log.error(utils.e2str(e))
                    self.setDone('error')
            # Execute python function?
            elif typ == 'f':
                if len(c[i]) < 2:
                    raise Exception('Need at least 2 items in custom-function (f) tuple')
                try:
                    args = {}
                    if len(c[i]) > 2: args = c[i][2]
                    args = self.reactor.resolveArgs(args, self.listener.activeChains[cid]['state'])
                    funres = c[i][1]({'event': self.event, 'cid': cid}, args)
                    target = None
                    if len(c[i]) > 3 and c[i][3]: target = c[i][3]
                    if target:
                        #log.debug("Update chain-state '%s' with function result: %s" % (target,funres))
                        self.listener.updateState(cid, 'event', funres, key=target)
                    #log.debug("ChainsFunction - Proceed with chain: %s" % cid)
                except StopRuleException, e:
                    #log.info("ChainsFunction - Stop chain on StopRuleException %s: %s" % (cid, c[i]))
                    #log.debug(utils.e2str(e))
                    self.setDone('func')
                except Exception, e:
                    log.error("Unhandled exception when running func %s in chain %s" % (c[i][0], cid))
                    log.error(utils.e2str(e))
                    self.setDone('error')
                """
            # Start/stop sequences?
            elif typ == 's':
                self.listener.startSequence(c[i][1], c[i][2])
            elif typ == 'S':
                self.listener.stopSequence(c[i][1], c[i][2], c[i][3])
                """
            # Hit an event? Stop processing.
            elif typ == 'e':
                break
            num += 1
            self.listener.activeChains[cid]['step'] += 1
            self.listener.activeChains[cid]['atime'] = time.time()
            if self.getDone():
                break

        # Pop off as many elements as we've processed
        if len(c) < num:
            log.warn('Strange: items_left_in_chain: %s vs pop_processed_items: %s - ignoring...' % (len(c), num))
        for i in range(num):
            try: c.pop(0)
            except: pass
        if len(c) == 0:
            self.setDone('endofchain')
        self.busy = False

    def getActionRpcChannel(self, deviceId):
        """
        log.debug('Get rpc channel: %s' % deviceId)
        if not self.actionRpcChannels.has_key(deviceId):
            log.debug('Make new rpc channel: %s' % deviceId)
            connection = amqp.Connection() # todo: clean up!
            self.actionRpcChannels[deviceId] = connection.rpc(
                keys = [ 'dr.%s.*' % deviceId, 'dx.%s.*' % deviceId ]
            )
            log.debug('Made new rpc channel: %s' % deviceId)
        log.debug('Return rpc channel: %s' % deviceId)
        return self.actionRpcChannels[deviceId]
        """
        connection = amqp.Connection() # todo: clean up!
        return connection.rpc(
            keys = [ 'dr.%s.*' % deviceId, 'dx.%s.*' % deviceId ],
            queuePrefix = 'rpc-reactor-worker'
        )

    def executeAction(self, a, cid, block, timeout):
        dev = a[1]
        cmd = a[2]
        args = a[3]
        state = self.listener.activeChains[cid]['state']
        args = self.listener.reactor.resolveArgs(args, state)
        try:
            if dev == None and cmd == 'sleep':
                log.info("ACTION-SLEEP: %s.%s(%s) STATE: %s" % (dev,cmd,args,state))
                time.sleep(float(args[0]))
                """ deprecated?
            elif dev == 'master':
                    log.info("ACTION-MASTER: %s.%s(%s) STATE: %s" % (dev,cmd,args,state))
                    name = 'on%s' % utils.ucfirst(cmd)
                    func = getattr(self.app, name)
                    return func(*args)
                """
            else:
                log.info("ACTION-DEVICE: %s.%s(%s) STATE: %s" % (dev,cmd,args,state))
                rpc = self.getActionRpcChannel(dev)
                #log.info('ACTION: got rpc channel: %s' % rpc)
                result = rpc.call('da.%s.%s' % (dev, cmd), args, timeout=timeout, block=block)
                rpc.close(closeConnection=True)
                return result

        #except NotConnectedException:
        #    log.info("Ignored command: %s because device: %s is not connected" % (cmd, dev))
        except amqp.TimeoutException, e:
            log.warn("Timeout while running action %s.%s" % (dev,cmd))
        except amqp.RemoteException, e:
            log.warn("Unhandled RemoteException caught in Chains.executeAction: %s, when running: %s(%s)" % (utils.e2str(e),cmd,args))
        except Exception:
            raise # foo fixme

