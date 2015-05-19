from chains.common import amqp, log

# todo: option for async (ie. no rpc, just push msg to amqp)
def Action(device, action, params=None):
    log.info("Run Action: %s.%s( %s )" % (device, action, params))
    if not params:
        params = []
    topic = 'da.%s.%s' % (device, action)
    connection = amqp.Connection()
    rpc = connection.rpc(queuePrefix='reactor-action')
    result = rpc.call(topic, data=params)
    try: rpc.close()
    except: pass
    try: connection.close()
    except: pass
