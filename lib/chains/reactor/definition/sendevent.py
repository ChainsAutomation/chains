from chains.common import amqp

def SendEvent(service, key, data):
    topic = '%s%s.%s.%s' % (amqp.PREFIX_SERVICE, amqp.PREFIX_EVENT, service, key)
    connection = amqp.Connection()
    producer = connection.producer(queueName='reactor-sendevent')
    event = {
        'service': service,
        'key':    key,
        'data':   data
    }
    producer.put(topic, event)
