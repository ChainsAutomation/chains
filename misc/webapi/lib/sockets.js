var socketio = require('socket.io');

module.exports = function(httpServer) {

	var self       = this;

	self.io		   = socketio.listen(httpServer, {log: false});
	self.sockets   = [];
	self.onMessage = null;
	self.enableDebug = false;


	self.setDebug = function(value) {
		self.enableDebug = value;
	}

	self.send = function(topic, data) {
		for(var i=0; i < self.sockets.length; i++) {
			self.sockets[i].debug('send: ' + topic, data);
			self.sockets[i].emit(topic, data);
		}
	}

	self.io.on('connection', function(socket) {

		socket.debug = function(message, data) {
			if (!self.debug)
				return;
			message = 'socket '
				+ this.handshake.address
				+ ' - '
				+ message;
			if (data)
				console.log('sockets: ' + message, data);
			else
				console.log('sockets: ' + message);
		}

		socket.debug('connected');

		self.sockets.push(socket);

		/* client => server, if we need that
		socket.on('printers', function(data) {
			self.debug('receive: printers = ', data);
			self.someCallback('printers', socket, data);
		});
		*/

		socket.on('disconnect', function () {
			socket.debug('disconnected');
			for(var i=0; i < self.sockets.length; i++) {
				if (self.sockets[i] == socket)
					self.sockets.splice(i, 1);
			}
		});

	});

}

