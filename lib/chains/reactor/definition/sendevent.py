from chains.common import amqp

def SendEvent(device, key, data):
    topic = 'de.%s.%s' % (device, key)
    connection = amqp.Connection()
    producer = connection.producer(queueName='reactor-sendevent')
    event = {
        'device': device,
        'key':    key,
        'data':   data
    }
    producer.put(topic, event)
