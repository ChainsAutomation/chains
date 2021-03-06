from __future__ import absolute_import
from __future__ import print_function
from chains.common import amqp

def SendEvent(service, key='nokey', data=None, device=None):
    topic = '%s%s.%s.%s' % (amqp.PREFIX_SERVICE, amqp.PREFIX_EVENT, service, key)
    connection = amqp.Connection()
    producer = connection.producer(queueName='reactor-sendevent')
    event = {
        'service': service,
        'device': device,
        'key':    key,
        'data':   data
    }
    producer.put(topic, event)
