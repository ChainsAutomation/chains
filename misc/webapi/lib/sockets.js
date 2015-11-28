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

	self.send = function(chainsTopic, data) {

        var tmp = chainsTopic.split('.');
        var prefix = tmp[0];
        var ioTopic = null;

        // todo: we may not want to push all of these to webgui
        // should add a system for saying what we want to subscribe to
        switch (prefix) {
            case 'se':
                ioTopic = 'service-event';
                break;
            case 'sa':
                ioTopic = 'service-action';
                break;
            case 'sr':
                ioTopic = 'service-action-response';
                break;
            case 'sh':
                ioTopic = 'service-heartbeat';
                break;
            case 'me':
                ioTopic = 'manager-event';
                break;
            case 'ma':
                ioTopic = 'manager-action';
                break;
            case 'mr':
                ioTopic = 'manager-action-response';
                break;
            case 'mh':
                ioTopic = 'manager-heartbeat';
                break;
            case 're':
                ioTopic = 'reactor-event';
                break;
            case 'ra':
                ioTopic = 'reactor-action';
                break;
            case 'rr':
                ioTopic = 'reactor-action-response';
                break;
            case 'rh':
                ioTopic = 'reactor-heartbeat';
                break;
            case 'H':
                ioTopic = 'hearbeat-request';
                break;
        }

        if (!ioTopic)
            return;

        //data['topic'] = chainsTopic;

		for(var i=0; i < self.sockets.length; i++) {
			self.sockets[i].debug('send: ' + ioTopic, data);
			self.sockets[i].emit(ioTopic, data);
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

