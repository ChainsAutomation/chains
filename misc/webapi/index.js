// Config

var host         = '0.0.0.0',
	port         = 7890,
	enableDebug  = false,
	enableNotice = false;

// Imports & init

var Sockets          = require('./lib/sockets'),
	Queue            = require('./lib/queue'),
	express          = require('express'),
	http             = require('http'),
	commander        = require('commander'),
    app              = express(),
	server           = http.createServer(app),
	queue            = new Queue(),
	sockets          = new Sockets(server),
	chains           = require('./lib/chains');


// Chains

chains.init(queue);
app.chains = chains;


// Common

function debug(msg, arg) {
	if (!enableDebug)
		return;
	if (arg)
		console.log('index: ' + msg, arg);
	else
		console.log('index: ' + msg);
}

function notice(msg, arg) {
	if (!enableNotice)
		return;
	if (arg)
		console.log('index: ' + msg, arg);
	else
		console.log('index: ' + msg);
}


// Command line args

commander
	.version('0.0.1')
	.option('-h, --host <host>', 'Listen to address (default = ' + host + ')')
	.option('-p, --port <port>', 'Listen to port (default = ' + port + ')')
	.option('-v, --verbose',     'Enable verbose output (default = false)')
	.option('-d, --debug',       'Enable very verbose output (default = false)')
	.parse(process.argv);

if (commander.host)
	host = commander.host;
if (commander.port)
	port = commander.port;
if (commander.verbose || commander.debug)
	enableDebug = true;
if (commander.debug)
	enableNotice = true;


// Queue

if (enableDebug)
	queue.setDebug(true);

queue.on('error', function(err) {
	process.exit(99);
});

queue.on('message', function(topic, message) {
	notice('forward message:', topic);
	try {
		sockets.send(topic, message);
	} catch (ex) {
		console.error('index: error forwarding message from rabbit to websockets: ', ex);
	}
});


// Sockets

if (enableDebug)
	sockets.setDebug(true);


// HTTP

require('./controllers/deviceStart')(app, '/devices/:deviceId/start');
require('./controllers/deviceStop')(app, '/devices/:deviceId/stop');
require('./controllers/devices')(app, '/devices');
require('./controllers/managers')(app, '/managers');
require('./controllers/reactors')(app, '/reactors');
require('./controllers/index')(app, '/');
//require('./controllers/devices')(app, '/devices');


// Start

queue.connect();

server.listen(port, host, function() {
	debug('express listening on ' + host + ':' + port);
});
