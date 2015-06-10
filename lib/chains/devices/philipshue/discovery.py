import urllib2, json

URL = 'https://www.meethue.com/api/nupnp'

def discover():
    response = urllib2.urlopen(URL)
    text = response.read()
    return json.loads(text)

if __name__ == '__main__':
    print discover()
