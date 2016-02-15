import json
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

URL = 'https://www.meethue.com/api/nupnp'

def discover():
    response = urllib2.urlopen(URL)
    text = response.read()
    return json.loads(text)

if __name__ == '__main__':
    print discover()
