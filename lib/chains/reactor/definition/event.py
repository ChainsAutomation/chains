import types

class Event:

    def __init__(self, service='*', device='*', key='*', data='*'):
        self.service = service
        self.device  = device
        self.key     = key
        self.data    = data

    # Check if this event is matched by "event" passed to this function
    # 
    # Be aware that what is "this" event and what is "event" does matter!
    # 
    # This event (ie. self) is the occuring event, and "event" passed to the function
    # is the event configured in the rule. That means "self" may have more data than
    # "event" and still match, but not vice versa. For details see _matchDict() below.
    #
    # Also note that "event" may be a list of event, in which case _one_ of them must
    # match (ie. OR operation). While "self" can (obviously) only be a single event.
    #
    # TL;DR: e1.match(e2) and e2.match(e1) may not give the same result!
    #
    def match(self, event):
        if type(event) == types.ListType:
            events = event
        else:
            events = [event]
        for event2 in events:
            if self._matchEvent(event2):
                return True
        return False
        
    # Match a single event
    def _matchEvent(self, event):
        for key in dir(self):
            if key[0] == '_': 
                continue
            val1 = self._tryattr(self, key)
            val2 = self._tryattr(event, key)
            if type(val1) == types.MethodType or type(val2) == types.MethodType:
                continue
            if not self._matchValues(val1,val2):
                return False
        return True

    def _matchValues(self, val1, val2):
        if val1 == val2: 
            return True
        if val1 == '*' or val2 == '*': 
            return True
        if type(val1) == types.DictType and type(val2) == types.DictType:
            return self._matchDicts(val1, val2)
        return False

    
    # d1 is this event (self), which is the occurring event
    # d2 is the event in the rule
    #
    # That means _all_ of d2's items must match d1's items,
    # but not all of d1's items must match d2's items.
    #
    # F.ex: The rule says:
    #   yield Event(service='foo', data={'value': 2})
    #
    # That should match this occuring event:
    #   Event(service='foo', data={'value': 2, 'type': 'humidity'})
    #
    # But if the rule says:
    #   yield Event(service='foo', data={'value': 2, 'type': 'humidity'})
    #
    # That should NOT match this occurring event:
    #   Event(service='foo', data={'value': 2})
    #
    def _matchDicts(self, d1, d2):
        for key in d2:
            v2 = d2[key]
            try:
                v1 = d1[key]
            except KeyError:
                return False
            if not self._matchValues(v1, v2):
                return False
        return True

    def _tryattr(self, obj, key):
        try: return getattr(obj, key)
        except AttributeError: return None

    def __str__(self):
        return '%s' % self.__dict__
