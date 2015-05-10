from chains.common import amqp

# todo: option for async (ie. no rpc, just push msg to amqp)
def Action(device, action, params=None):
    if not params:
        params = []
    topic = 'da.%s.%s' % (device, action)
    connection = amqp.Connection()
    rpc = connection.rpc(queuePrefix='reactor-action')
    return rpc.call(topic, data=params)
