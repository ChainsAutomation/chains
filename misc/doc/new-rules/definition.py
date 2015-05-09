import time

class Action:

    def __init__(self, device, action, params=None):
        self.device = device
        self.action = action
        self.params = params
        debug("Action", self)
        time.sleep(2)
        debug("- action done")


class Event:

    def __init__(self, **kw):
        for key in kw:
            setattr(self, key, kw[key])

    # quick'n'dirty matching for testing
    # probably needs some l0ve to work in production

    # Match one of the passed events
    def match(self, event): # event can be 1 Event or list of events
        if type(event) == types.ListType:
            events = event
        else:
            events = [event]
        for event2 in events:
            if self.matchEvent(event2):
                return True
        return False
        
    # Match a single event
    def matchEvent(self, event):
        for key in dir(self):
            if key[0] == '_': 
                continue
            val1 = self.tryattr(self, key)
            val2 = self.tryattr(event, key)
            if type(val1) == types.MethodType or type(val2) == types.MethodType:
                continue
            if not self.matchValues(val1,val2):
                return False
        return True

    def matchValues(self, val1, val2):
        if val1 == val2: return True
        if val1 == '*' or val2 == '*': return True
        return False

    def tryattr(self, obj, key):
        try: return getattr(obj, key)
        except AttributeError: return None

    def __str__(self):
        return '%s' % self.__dict__

# temp start
import json, types
def debug(msg, data=None):
    if data:
        if type(data) == types.InstanceType:
            data = data.__dict__
        elif type(data) == types.ListType:
            tmp = []
            for item in data:
                tmp.append(item.__dict__)
            data = tmp
        msg += ' ' + json.dumps(data)
    print "DEBUG: %s" % msg
# temp end
