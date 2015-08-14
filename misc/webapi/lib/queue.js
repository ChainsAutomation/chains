var exchangeName    = 'chains',
    queueName       = 'chains.websockets',
    amqp            = require('amqp');

function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

module.exports = function(bindTopic) {

    var self = this;

    self.connection = null;
    self.onClose = null;
    self.onError = null;
	self.onReady = null;
    self.onMessage = {};
    self.connection = null;
	self.exchange = null;
    self.enableDebug = false;

    self.on = function(evt, callback) {
		var id = guid();
        switch (evt) {
            case 'close':
                self.onClose = callback;
                break;
            case 'error':
                self.onError = callback;
                break;
			case 'ready':
				self.onReady = callback;
				break;
            case 'message':
                self.onMessage[id] = callback;
                break;
            default:
                throw 'no such event: ' + evt;
        }
		return id;
    }

	self.off = function(evt, id) {
        switch (evt) {
            case 'message':
				delete self.onMessage[id];
                break;
        }
	}

    self.publish = function(topic, message, correlationId) {
        if (!self.exchange)
            throw 'not connected yet';
		message = JSON.stringify(message);
		self.exchange.publish(topic, message, {contentType: 'application/json', correlationId: correlationId});
    }

/* todo
	self.disconnect = function() {
		self.connection.disconnect();
		delete self.connection;
	}
*/

    self.connect = function() {

        self.debug('connecting');

        self.connection = amqp.createConnection();

        self.connection.on('close', function() {
            self.debug('connection closed');
            if (self.onClose)
                self.onClose();
        });

        self.connection.on('error', function(err) {
            console.error('amqp: error ', err);
            if (self.onError)
                self.onError(err);
        });

        self.connection.on('ready', function () {

            self.debug('connection ready');

            self.connection.exchange(
                exchangeName,
                {
                    durable: false,
                    type: 'topic',
                    autoDelete: true
                },
                function (exchange) {

                    self.debug('exchange ready: ' + exchange.name);
					self.exchange = exchange;

                    self.connection.queue(
                        queueName,
                        {
                            durable: false,
                            autoDelete: false
                        },
                        function(q) {

                            self.debug('queue ready: ' + q.name);

							var thisBindTopic = bindTopic || '#';

							q.bind(exchange, thisBindTopic, function() {

								self.debug('queue bound to exchange with topic: ' + thisBindTopic);

								if (self.onReady)
									self.onReady();

                            	q.subscribe(
                                	{ ack: false },
                                	function (message, xxx, attribs) {
                                    	//self.debug('received message: ' + attribs.routingKey + ' =', message);
										for (var key in self.onMessage) {
											//self.debug('callback: ' + key, attribs.routingKey);
                                        	self.onMessage[key](attribs.routingKey, message, attribs);
										}
                                	}
                            	);

							});

                        }
                    );


                }
            );

        });

    }

    self.setDebug = function(value) {
        self.enableDebug = value;
    }

    self.debug = function(msg, arg) {
        if (!self.enableDebug)
            return;
        msg = 'amqp: ' + msg;
        if (arg)
            console.log(msg, arg);
        else
            console.log(msg);
    }


}

