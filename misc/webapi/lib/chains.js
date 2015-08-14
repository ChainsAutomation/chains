// todo:
// - use existing connection
// - clean up (unbind queue, connection if not existing, etc)
// - timeout for rpc

var queue       = null,
    RPC_TIMEOUT = 2000;

function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

module.exports.init = function(_queue) {
	queue = _queue;
}

module.exports.rpc = function(daemonType, daemonId, command, args, callback) {

	if (!queue)
		throw 'no queue set yet';

	var status = null;
	var requestTopic  = daemonType + 'a.' + daemonId + '.' + command;
	var responseTopic = daemonType + 'r.' + daemonId + '.' + command;
	var errorTopic    = daemonType + 'x.' + daemonId + '.' + command;

	var correlationId = guid();

	var callbackId = queue.on('message', function(topic, message, attribs){

console.log('RECV:',topic,attribs.correlationId);
		if (attribs.correlationId != correlationId)
			return;

		var error = null;
		if (topic == errorTopic) {
			error = true;
		} else if (topic == responseTopic) {
			error = false;
		} else {
			return;
		}

console.log('- RECV YES');
		queue.off('message', callbackId);
		status = 'success';

		if (error) {
console.log('ERR:',message);
			var errorMessage = '';
			if (message) {
				if (typeof(message) == 'string')
					errorMessage = message;
				else
					errorMessage = JSON.stringify(message);
			} else {
				errorMessage = 'undefined error';
			}
			callback(errorMessage, null);
		} else {
			callback(null, message);
		}


	});
	//queue.setDebug(true);

	setTimeout(
		function(){
			if (status)
				return;
			console.log('chains.rpc - TIMEOUT');
			queue.off('message', callbackId);
			//queue.disconnect(); // todo
			status = 'timeout';
			callback('Timeout', null);
		},
		RPC_TIMEOUT
	);

	console.log('publish:',requestTopic, correlationId);
	queue.publish(requestTopic, args, correlationId);

}


module.exports.callOrchestratorAction = function(command, args, callback) {
	module.exports.rpc('o', 'main', command, args, callback);
}

module.exports.callManagerAction = function(id, command, args, callback) {
	module.exports.rpc('m', id, command, args, callback);
}

module.exports.callReactorAction = function(id, command, args, callback) {
	module.exports.rpc('r', id, command, args, callback);
}

module.exports.callDeviceAction = function(id, command, args, callback) {
	module.exports.rpc('d', id, command, args, callback);
}

