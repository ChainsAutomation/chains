'''
Various util-functions.

Some of these should possibly be moved somewhere else and
some may not be needed (anymore), but we can clean that up
later.
'''

import os, traceback, re, time, socket, imp

# Import and instantiate an object from a package dynamically / thru reflection.
def newObject(pkgName, className, isReload=False, args=None, path=None):
    pkg = pkgName.split('.')
    str = ''
    for p in pkg:
        if str != '': str += '.'
        str += p
    if path:
        i = imp.load_source(str, path)
    else:
        i = __import__(str)
        pkg = pkg[1:]
        for p in pkg:
            i = getattr(i, p)
    if isReload:
        reload(i)
    clazz = getattr(i, className)
    if args:
        obj = apply(clazz, args)
    else:
        obj = apply(clazz)
    return obj

def lcfirst(a):
    return "%s%s" % (a[:1].lower(), a[1:])
def ucfirst(a):
    return "%s%s" % (a[:1].upper(), a[1:])

# @todo: show errno if available
def e2str(e):
    tb = traceback.format_exc(e)
    return '%s: %s\n%s' % (e.__class__, e.message, tb)

def stripTags(value, stripLF=False):
    value = re.sub(r'<[^>]*?>', '', value)
    if stripLF:
        value = value.replace('\r', '')
        value = value.replace('\n', ' ')
    return value

def fetchurl(url, username=None, password=None, postdata=None, headers=None, gethandle=False):
    # Params / init
    tmp = url.split('://')
    prot = tmp.pop(0)
    url = '://'.join(tmp)
    domain = url.split('/')[0]
    if not headers: headers = {}
    import urllib2

    # Also support username/pw in url itself
    tmp = domain.split('@')
    if len(tmp) > 1:
        username, password = tmp[0].split(':')
        domain = tmp[1]
        tmp2 = url.split('/')
        tmp2[0] = domain
        url = '/'.join(tmp2)

    # Authentication (optional)
    if username:
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, domain, username, password)
        opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman))
        urllib2.install_opener(opener)

    # Open url
    r = urllib2.Request('%s://%s' % (prot, url), postdata, headers)
    u = urllib2.urlopen(r)

    # Return filehandle
    if gethandle: return u

    # Or data
    data = u.readlines()
    u.close()
    return data

def formatDuration(val):
    m = 60
    h = m*m
    d = h*24
    w = d*7
    tim = [m,h,d,w]
    txt = ['m','h','d','w']
    for j in range(len(txt)):
        i = len(txt)-j-1
        if val >= tim[i]:
            #return '%s %s' % (formatDecimals(float(val)/float(tim[i])), txt[i])
            return '%s %s' % ( formatDecimals(val/tim[i]), txt[i] )
    return '%ss' % formatDecimals(val)

def formatDecimals(val, decimals=2):
    val = str(val)
    tmp = val.split('.')
    i = tmp[0]
    if decimals < 1: return i
    d = '00'
    try: d = tmp[1]
    except: pass
    for n in range(decimals-len(d)):
        d += '0'
    return '%s.%s' % (i, d[:decimals])


def formatTime(t, skipSec=False):
    if not t: return 'Never'
    t = time.localtime(float(t))
    # Time always
    fmt = '%H:%M:%S'
    if skipSec: fmt = '%H:%M'
    # Date if now today
    if time.strftime('%Y-%m-%d',t) != time.strftime('%Y-%m-%d',time.localtime(time.time())):
        fmt = '%Y-%m-%d ' + fmt
    return time.strftime(fmt, t)

def getHostName():
    return socket.gethostname()

def caseSplit(txt, lcFirst=True, firstOnly=False):
    result = []
    buf = ''
    started = False
    done = False
    for c in txt:
        if done:
            buf += c
            continue
        if started:
            if c.upper() == c:
                result.append(buf)
                if lcFirst:
                    buf = c.lower()
                else:
                    buf = c
                if firstOnly:
                    done = True
            else:
                buf += c
        else:
            started = True
            if lcFirst:
                buf += c.lower()
            else:
                buf += c
    result.append(buf)
    return result


