from chains.common import amqp, log

# todo: option for async (ie. no rpc, just push msg to amqp)
def Action(service, action, params=None):

    rpc        = None
    connection = None

    try:
        log.info("Run Action: %s.%s( %s )" % (service, action, params))
        if not params:
            params = []
        topic = '%s%s.%s.%s' % (amqp.PREFIX_SERVICE, amqp.PREFIX_ACTION, service, action)
        connection = amqp.Connection()
        rpc = connection.rpc(queuePrefix='reactor-action')
        result = rpc.call(topic, data=params)
    except Exception, e:
        try:
            log.error("Exception in action %s.%s: %s" % (service,action,e))
        except:
            pass

    try: rpc.close()
    except: pass
    try: connection.close()
    except: pass
