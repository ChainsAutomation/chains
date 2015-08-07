# -*- coding: utf-8 -*-
import socket
import json
import time

# import requests_unixsocket
# import requests
# requests_unixsocket.monkeypatch()
# r = requests.get('http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/')


def pretty(jobj):
    print json.dumps(jobj, sort_keys=True, indent=4, separators=(',', ': '))


