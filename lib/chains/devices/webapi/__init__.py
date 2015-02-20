# Run as uwsgi app:
# uwsgi --http :8000 --wsgi-file /srv/chains/lib/chains/devices/webapi/__init__.py --callable app --master --processes 1 -l 50 -L
# <stian> i think we also need: --enable-threads
# Options:
# -l : listen queue size
# -p|--processes : number of uwsgi processes to start
# -L : disable logging

#import simplejson as json
#import cjson as json
import json
import falcon
import urlparse
import chains.device
import chains.common.amqp as amqp
from chains.common import log


# =======================================================
# Chains device stuff
# todo: possibly split into its own file later?
# =======================================================


DEVICE = None  # Global ref to chains device object


class WebApiDevice(chains.device.Device):
    """
    A normal chains device for the webapi

    Per now, we only use this to communicate with amqp, so we don't need to 
    implement anything here.

    But in principle we could add actions and do all kinds of normal device stuff.
    """
    pass


def getDevice():

    """
    Get chains-device object if already created, or create it

    If we create it during startup, we seem to run into concurrency/locking issues
    of some sort (sometimes stuff will work, other times amqp-calls will lock forever).

    It seems device must be created _after_ usgwi init is complete. And since I cannot find
    a hook for when this happens, we'll just create the device first time it's needed instead.

    This was we know that uswgi is up and running first, since someone made a web request that
    needs the device object first.
    """

    global DEVICE
    if not DEVICE:

        # Because we're not started by orchestrator, we don't have our config.
        # We can get it by calling orchestrator.getDeviceConfig(id), but we don't
        # know our id since that's in the config.
        # But for now, we don't need any config, so we'll figure this out later.
        deviceConfig = chains.device.config.DeviceConfig(data={
            'main': {
                'id':      'todo-unique-id-for-webapi',
                'class':   'WebApi',
                'name':    'webapi',
                'manager': 'webapi'
            }
        })
        DEVICE = WebApiDevice(deviceConfig)

    return DEVICE


# =======================================================
# Utils
# =======================================================

def getBaseUrl(req):
    parsed = urlparse.urlsplit(req.url)
    return '%s://%s' % (parsed.scheme, parsed.netloc)


# =======================================================
# Falcon resource classes
# todo: possibly split into one file for each resource later?
# =======================================================


class Index(object):

    def on_get(self, req, resp):
        baseUrl = getBaseUrl(req)
        resp.status = falcon.HTTP_200
        resp.content_type = 'application/json'
        index_content = [
            {
                "_links":
                {
                    "self": {"href": "%s/devices" % baseUrl}
                },
                "id": "devices",
                "name": "Devices"
            },
            {
                "_links":
                {
                    "self": {"href": "%s/managers" % baseUrl}
                },
                "id": "managers",
                "name": "Managers"
            },
        ]
        resp.body = json.dumps(index_content)


class Devices(object):

    def on_get(self, req, res):

        # fetch device list from orchestrator
        result = []
        devices = getDevice().callOrchestratorAction('getDevices')
        for deviceId in devices:

            # device item from orchestrator contains a lot of stuff, 
            # f.ex. full device config, but that's a bit overkill here.
            # so only pick the stuff that's interessting
            device = devices[deviceId]
            main   = device.get('main') # this is [main] from config
            if not main: main = {}

            result.append({
                'id':        deviceId,
                'name':      main.get('name'),
                'class':     main.get('class'),
                'online':    device.get('online'),
                'heartbeat': device.get('heartbeat'),
                'manager':   main.get('manager'),
                'autostart': main.get('autostart')
            })

        res.status        = falcon.HTTP_200
        res.cache_control = ['no-cache']
        res.content_type  = 'application/json'
        res.body          = json.dumps(result)

class DeviceStart(object):

    def on_post(self, req, res, deviceId):

        res.content_type  = 'application/json'
        res.cache_control = ['no-cache']

        try:
            getDevice().callOrchestratorAction('startDevice', [deviceId])
            res.status        = falcon.HTTP_200
            res.body          = json.dumps({'status': True, 'error': None})
        except Exception, e:
            res.status        = falcon.HTTP_500
            res.body          = json.dumps({'status': False, 'error': '%s'%e})


class DeviceStop(object):

    def on_post(self, req, res, deviceId):

        res.content_type  = 'application/json'
        res.cache_control = ['no-cache']

        try:
            getDevice().callOrchestratorAction('stopDevice', [deviceId])
            res.status        = falcon.HTTP_200
            res.body          = json.dumps({'status': True, 'error': None})
        except Exception, e:
            res.status        = falcon.HTTP_500
            res.body          = json.dumps({'status': False, 'error': '%s'%e})



class Managers(object):

    def on_get(self, req, res):

        result = []
        managers = getDevice().callOrchestratorAction('getManagers')
        for managerId in managers:
            manager = managers[managerId]
            result.append({
                'id':        managerId,
                'online':    manager.get('online'),
                'heartbeat': manager.get('heartbeat')
            })

        res.status        = falcon.HTTP_200
        res.cache_control = ['no-cache']
        res.content_type  = 'application/json'
        res.body          = json.dumps(result)


class State(object):

    def on_get(self, req, res, deviceId=None, key=None, path=None):

        args   = []
        result = []

        fixDataDepth = 0
        if deviceId:
            args.append(deviceId)
            fixDataDepth = 1
            if key:
                args.append(key)
                args.append('data')
                fixDataDepth = False
                if path:
                    args.append(path)
        if args:
            args = ['.'.join(args)]

        data = getDevice().callReactorAction('master', 'getState', args)
        if fixDataDepth != False:
            data = self.fixData(data, fixDataDepth)

        res.status        = falcon.HTTP_200
        res.cache_control = ['no-cache']
        res.content_type  = 'application/json'
        res.body          = json.dumps(data)

    # State contains a "data" step, like this:
    # State.<deviceid>.<key>.data.<value>
    # We don't want that in response here, so fix it
    # Actually, we may not want it in state at all, but that's a fix for another day
    def fixData(self, data, depth):
        result = {}

        if depth == 0:
            for deviceId in data:
                result[deviceId] = {}
                for key in data[deviceId]:
                    result[deviceId][key] = {}
                    for subkey in data[deviceId][key]['data']:
                        result[deviceId][key][subkey] = data[deviceId][key]['data']

        elif depth == 1:
            for key in data:
                result[key] = {}
                for subkey in data[key]['data']:
                    result[key][subkey] = data[key]['data']

        else:
            raise Exception('Cannot handle depth: %s' % depth)

        return result


# =======================================================
# Falcon initialization
# =======================================================

api = app = application = falcon.API()

# Resources
index = Index()
managers = Managers()
devices = Devices()
deviceStart = DeviceStart()
deviceStop = DeviceStop()
state = State()

api.add_route('/', index)
api.add_route('/managers', managers)
api.add_route('/devices', devices)
api.add_route('/devices/{deviceId}/start', deviceStart)
api.add_route('/devices/{deviceId}/stop', deviceStop)

# a bit hacky but i don't know how to do optional parameters with falcon routes...
api.add_route('/state', state)
api.add_route('/state/{deviceId}', state)
api.add_route('/state/{deviceId}/{key}', state)
api.add_route('/state/{deviceId}/{key}/{path}', state)
