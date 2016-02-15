from __future__ import absolute_import
from six.moves import range


class State:

    def __init__(self):
        self.data = {}

    def __getitem__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self.set(*args, **kwargs)

    def set(self, key, value):
        key = key.split('.')
        data = self.data
        for i in range(len(key) - 1):
            if key[i] not in data:
                data[key[i]] = {}
            data = data[key[i]]
        data[key[-1:][0]] = value

    def get(self, key=None):
        if not key:
            return self.data
        key = key.split('.')
        data = self.data
        try:
            for k in key:
                data = data[k]
            return data
        except KeyError:
            return None

    def delete(self, key=None):
        if not key:
            self.data = {}
            return
        key = key.split('.')
        data = self.data
        for i in range(len(key) - 1):
            if key[i] not in data:
                data[key[i]] = {}
            data = data[key[i]]
        del data[key[-1:][0]]
