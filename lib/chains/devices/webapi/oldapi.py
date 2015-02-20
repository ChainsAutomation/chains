from chains.common import log
from chains.device import Device
from chains.common import amqp
from chains import commandline
from chains.commandline import formatter
import sys
import web

_device = None

class WebApiDevice(Device):

    def onInit(self):
        global _device
        _device = self
        #self.interval = self.config.getInt('interval')

    def onStart(self):
        log.info('webapi.onStart - start')
        urls = (
            '/',                    'WebApiIndex',
            '/rpc/(.*)',            'WebApiRpc',
            '/rpc',                 'WebApiRpc',
        )
        sys.argv = [self.config.get('host'), self.config.get('port')]
        #sys.argv = ['localhost', '9001']
        app = web.application(urls, globals(), autoreload=False)
        log.info('webapi.onStart - go run app')
        app.run()
        log.info('webapi.onStart - done (exit?)')

class WebApiBase:
    def getDevice(self):
        global _device
        return _device
    """
    def GET(self, *args):
        return self._main(args, web.input())
    def POST(self, *args):
        return self._main(args, web.input())
    def _main(self, args, kw):
        self.main(args, kw)
    def main(self, args, kw):
        return '(unimplemented)'
    """

class WebApiIndex(WebApiBase):
    def GET(self, *args):
        return '<h1>Chains</h1><a href="/rpc/">rpc</a>'

class WebApiRpc:
    def GET(self, *args):
        if len(args) < 1 or args[0].strip() == '':
            return '''
            <h1>Chains RPC</h1>
            This is the Chains HTTP API
            <h2>Quick start examples</h2>
            <table>
             <tr>
              <td>List devices</td>
              <td><a href="/rpc/device/list">/rpc/device/list</a></td>
             </tr>
             <tr>
              <td>Run echo action in device test with argument foo</td>
              <td><a href="/rpc/device/action/test/echo/foo">/rpc/device/action/test/echo/foo</a></td>
             </tr>
             <tr>
              <td>List managers</td>
              <td><a href="/rpc/manager/list">/rpc/manager/list</a></td>
             </tr>
             <tr>
              <td>List managers as JSON</td>
              <td><a href="/rpc/manager/list?format=json">/rpc/manager/list?format=json</a></td>
             </tr>
            </table>
            <h2>Full list of available commands</h2>
            <pre>''' + commandline.help() + '''</pre>
            '''
        args = args[0].split('/')
        section = args.pop(0)
        command = args.pop(0)
        cmd = commandline.getCommandObject(section, command)
        try:
            log.info('cmd1')
            result = cmd.main(*args)
            log.info('cmd2')
            opt = web.input()
            log.info('cmd3')
            if opt.has_key('format') and opt['format'] == 'json':
                fmt = formatter.load('json')
            elif opt.has_key('format') and opt['format'] == 'raw':
                fmt = formatter.load('generic')
            else:
                fmt = formatter.load(cmd.getFormatter())
            output = fmt.main(result)
            log.info('cmd4')

            web.header('Content-Type', 'application/json')
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Credentials', 'true')

            return output
        finally:
            log.info('cmd-finally-1')
            cmd.close()
            log.info('cmd-finally-2')

    def getBoolOpt(self, key):
        opt = web.input()
        if opt.has_key(key) and opt[key] and opt[key] not in ['','0']:
            return True
        else:
            return False

    def rpcCall(self, topic, args):
        log.info('webapi.rpc - start')
        #conn = amqp.Connection()
        conn = self.connection
        log.info('webapi.rpc - got conn')
        rpc = conn.rpc()
        log.info('webapi.rpc - got rpc: %s' % rpc)
        try:
            log.info('webapi.rpc - call 1: %s = %s' % (topic,args))
            res = rpc.call(topic, args, timeout=10)
            log.info('webapi.rpc - call 2: '%res)
            return res
        finally:
            log.info('webapi.rpc - close rpc 1')
            rpc.close()
            log.info('webapi.rpc - close rpc 2')
            conn.close()
            log.info('webapi.rpc - close rpc 3')
        
