var exchangeName    = 'chains',
    queueName       = 'chains.websockets',
    amqp            = require('amqp');

module.exports = function(callback) {

    var self = this;

    self.connection = null;
    self.onClose = null;
    self.onError = null;
	self.onReady = null;
    self.onMessage = null;
    self.connection = null;
	self.exchange = null;
    self.enableDebug = false;

    self.on = function(evt, callback) {
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
                self.onMessage = callback;
                break;
            default:
                throw 'no such event: ' + evt;
        }
    }

    self.publish = function(topic, message) {
        if (!self.exchange)
            throw 'not connected yet';
		message = JSON.stringify(message);
		self.exchange.publish(topic, message, {contentType: 'application/json'});
    }

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

							q.bind(exchange,'#', function() {

								self.debug('queue bound to exchange');

								if (self.onReady)
									self.onReady();

                            	q.subscribe(
                                	{ ack: false },
                                	function (message, xxx, attribs) {
                                    	//self.debug('received message: ' + attribs.routingKey + ' =', message);
                                    	if (self.onMessage)
                                        	self.onMessage(attribs.routingKey, message);
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

