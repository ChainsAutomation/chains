var exchangeName    = 'chains',
    queueName       = 'chains.websockets',
    express         = require('express'),
    http            = require('http'),
    app             = express(),
    server          = http.createServer(app);
    amqp            = require('amqp'),
    fs              = require('fs');


// Express

app.use(express.errorHandler({ dumpExceptions: true, showStack: true }));
app.use(app.router);

// For demo purposes only, can safely be commented out
app.use('/demo', express.static(__dirname + '/static/demo'));


// AMQP

var Queue = function(amqp, onMessage) {

    var connection = amqp.createConnection();

    console.log('amqp connecting');

    connection.on('close', function(a,b) {
        console.log('amqp connection closed',a,b);
    });

    connection.on('error', function(a,b) {
        console.log('amqp connection error',a,b);
        process.exit();
    });

    connection.on('ready', function () {

        console.log('amqp connection ready');

        connection.exchange(
            exchangeName,
            {
                durable: false,
                type: 'topic',
                autoDelete: true
            },
            function (exchange) {
                console.log('amqp exchange ready', exchange.name);

                connection.queue(
                    queueName,
                    {
                        durable: false,
                        autoDelete: false
                    },
                    function(q) {

                        console.log('amqp queue ready');

                        q.subscribe(
                            { ack: false },
                            function (message, xxx, attribs) {
                                //console.log('amqp received message: ' + attribs.routingKey + ' =', message);
                                onMessage(attribs.routingKey, message);
                            }
                        );

                    }
                );


            }
        );

    });

}


// Sockets
// List of connected socket.io clients, and function to broadcast

var Sockets = function(io) {

    var self = this;

    self.io      = io;
    self.sockets = [];


    self.send = function(topic, data) {
        for(var i=0; i < self.sockets.length; i++) {
            self.sockets[i].debug('send: ' + topic, data);
            self.sockets[i].emit(topic, data);
        }
    }


    self.io.on('connection', function(socket) {

        socket.debug = function(message, data) {
            message = 'socket '
                + this.handshake.address.address
                + ':'
                + this.handshake.address.port
                + ' - '
                + message;
            if (data)
                console.log(message, data);
            else
                console.log(message);
        }

        socket.debug('connected');

        self.sockets.push(socket);

        socket.on('disconnect', function () {
            socket.debug('disconnected');
            for(var i=0; i < self.sockets.length; i++) {
                if (self.sockets[i] == socket)
                    self.sockets.splice(i, 1);
            }
        });

    });

}


// Routes

app.get('/', function(req, res) {
    res.send('Nothing to see, please move along...');
});


// Main

var io = require('socket.io').listen(server, {log: false});
var sockets = new Sockets(io);

// When AMQP message arrives
var queue = new Queue(amqp, function(routingKey, message) {
    try {
		var key = routingKey.split('.');
		if (key[0] == 'de' && key[2] != 'online')
        	sockets.send('device-event', message);
		else if (key[0] == 'de' && key[2] == 'online')
			sockets.send('daemon-status', {
				type: 'device',
				id: message.device,
				value: message.data.value
			});
		else if (key[0] == 'me' && key[2] == 'online')
			sockets.send('daemon-status', {
				type: 'manager',
				id: message.host,
				value: message.data.value
			});
		else if (key[0] == 're' && key[2] == 'online')
			sockets.send('daemon-status', {
				type: 'reactor',
				id: message.host,
				value: message.data.value
			});
    } catch (e) {
        console.error('error proxying message to socket(s)', e);
    }
});


server.listen(3001, '0.0.0.0', function() {
    console.log('express listening on port 3001');
});

